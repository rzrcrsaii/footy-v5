"""
Footy-Brain v5 Fixtures Router
REST API endpoints for fixture data with filtering and pagination.
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc
from pydantic import BaseModel, Field

from apps.api_server.deps import get_db_session, get_optional_user, api_rate_limit
from apps.api_server.db.models import Fixture, League, Team, Venue

# Import fixture detail services
from tools.fixture_statistics_service import FixtureStatisticsService
from tools.fixture_lineups_service import FixtureLineupsService
from tools.fixture_events_service import FixtureEventsService
from tools.fixture_h2h_service import FixtureH2HService
from tools.fixture_player_statistics_service import FixturePlayerStatisticsService

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class FixtureResponse(BaseModel):
    """Fixture response model."""
    
    id: int
    referee: Optional[str]
    timezone: Optional[str]
    date: datetime
    timestamp: Optional[int]
    
    # Status
    status_short: str
    status_long: Optional[str]
    status_elapsed: Optional[int]
    status_extra: Optional[int]
    
    # League and season
    league_id: int
    league_name: Optional[str]
    season_year: int
    round: Optional[str]
    
    # Teams
    home_team_id: int
    home_team_name: Optional[str]
    home_team_logo: Optional[str]
    away_team_id: int
    away_team_name: Optional[str]
    away_team_logo: Optional[str]
    
    # Scores
    home_goals: int
    away_goals: int
    home_goals_ht: int
    away_goals_ht: int
    home_goals_et: int
    away_goals_et: int
    home_goals_pen: int
    away_goals_pen: int
    
    # Venue
    venue_id: Optional[int]
    venue_name: Optional[str]
    venue_city: Optional[str]
    
    # Metadata
    created_at: datetime
    updated_at: datetime


class FixtureListResponse(BaseModel):
    """Paginated fixture list response."""
    
    fixtures: List[FixtureResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool


class FixtureFilters(BaseModel):
    """Fixture filtering parameters."""
    
    league_id: Optional[int] = None
    season_year: Optional[int] = None
    team_id: Optional[int] = None
    status: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    round: Optional[str] = None
    venue_id: Optional[int] = None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def build_fixture_query(filters: FixtureFilters):
    """Build SQLAlchemy query with filters."""
    # Create aliases for teams
    home_team = Team.__table__.alias("home_team")
    away_team = Team.__table__.alias("away_team")

    query = select(
        Fixture,
        League.name.label("league_name"),
        home_team.c.name.label("home_team_name"),
        home_team.c.logo.label("home_team_logo"),
        away_team.c.name.label("away_team_name"),
        away_team.c.logo.label("away_team_logo"),
        Venue.name.label("venue_name"),
        Venue.city.label("venue_city")
    ).select_from(
        Fixture
        .join(League, Fixture.league_id == League.id)
        .join(home_team, Fixture.home_team_id == home_team.c.id)
        .join(away_team, Fixture.away_team_id == away_team.c.id)
        .outerjoin(Venue, Fixture.venue_id == Venue.id)
    )
    
    conditions = []
    
    if filters.league_id:
        conditions.append(Fixture.league_id == filters.league_id)
    
    if filters.season_year:
        conditions.append(Fixture.season_year == filters.season_year)
    
    if filters.team_id:
        conditions.append(
            or_(
                Fixture.home_team_id == filters.team_id,
                Fixture.away_team_id == filters.team_id
            )
        )
    
    if filters.status:
        conditions.append(Fixture.status_short == filters.status)
    
    if filters.date_from:
        conditions.append(Fixture.date >= filters.date_from)
    
    if filters.date_to:
        # Add one day to include the entire day
        date_to_end = datetime.combine(filters.date_to, datetime.max.time())
        conditions.append(Fixture.date <= date_to_end)
    
    if filters.round:
        conditions.append(Fixture.round == filters.round)
    
    if filters.venue_id:
        conditions.append(Fixture.venue_id == filters.venue_id)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    return query


def format_fixture_response(row) -> FixtureResponse:
    """Format database row to FixtureResponse."""
    fixture = row[0]  # Fixture object
    
    return FixtureResponse(
        id=fixture.id,
        referee=fixture.referee,
        timezone=fixture.timezone,
        date=fixture.date,
        timestamp=fixture.timestamp,
        status_short=fixture.status_short,
        status_long=fixture.status_long,
        status_elapsed=fixture.status_elapsed,
        status_extra=fixture.status_extra,
        league_id=fixture.league_id,
        league_name=row.league_name,
        season_year=fixture.season_year,
        round=fixture.round,
        home_team_id=fixture.home_team_id,
        home_team_name=row.home_team_name,
        home_team_logo=row.home_team_logo,
        away_team_id=fixture.away_team_id,
        away_team_name=row.away_team_name,
        away_team_logo=row.away_team_logo,
        home_goals=fixture.home_goals,
        away_goals=fixture.away_goals,
        home_goals_ht=fixture.home_goals_ht,
        away_goals_ht=fixture.away_goals_ht,
        home_goals_et=fixture.home_goals_et,
        away_goals_et=fixture.away_goals_et,
        home_goals_pen=fixture.home_goals_pen,
        away_goals_pen=fixture.away_goals_pen,
        venue_id=fixture.venue_id,
        venue_name=row.venue_name,
        venue_city=row.venue_city,
        created_at=fixture.created_at,
        updated_at=fixture.updated_at
    )


# =============================================================================
# API ENDPOINTS
# =============================================================================

@router.get("/", response_model=FixtureListResponse)
async def get_fixtures(
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    
    # Sorting
    sort_by: str = Query("date", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    
    # Filters
    league_id: Optional[int] = Query(None, description="Filter by league ID"),
    season_year: Optional[int] = Query(None, description="Filter by season year"),
    team_id: Optional[int] = Query(None, description="Filter by team ID (home or away)"),
    status: Optional[str] = Query(None, description="Filter by match status"),
    date_from: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    round: Optional[str] = Query(None, description="Filter by round"),
    venue_id: Optional[int] = Query(None, description="Filter by venue ID"),
    
    # Dependencies
    db: AsyncSession = Depends(get_db_session),
    user: Optional[Dict] = Depends(get_optional_user),
    rate_limit: None = Depends(api_rate_limit)
):
    """
    Get fixtures with filtering, sorting, and pagination.
    
    Returns a paginated list of fixtures with team, league, and venue information.
    """
    try:
        # Build filters
        filters = FixtureFilters(
            league_id=league_id,
            season_year=season_year,
            team_id=team_id,
            status=status,
            date_from=date_from,
            date_to=date_to,
            round=round,
            venue_id=venue_id
        )
        
        # Build base query
        query = build_fixture_query(filters)
        
        # Add sorting
        sort_column = getattr(Fixture, sort_by, Fixture.date)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Count total results
        count_query = select(Fixture.id).select_from(
            build_fixture_query(filters).subquery()
        )
        total_result = await db.execute(count_query)
        total = len(total_result.fetchall())
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        # Execute query
        result = await db.execute(query)
        rows = result.fetchall()
        
        # Format response
        fixtures = [format_fixture_response(row) for row in rows]
        
        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        return FixtureListResponse(
            fixtures=fixtures,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        logger.error(f"Error fetching fixtures: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{fixture_id}", response_model=FixtureResponse)
async def get_fixture(
    fixture_id: int,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[Dict] = Depends(get_optional_user),
    rate_limit: None = Depends(api_rate_limit)
):
    """
    Get a specific fixture by ID.
    
    Returns detailed information about a single fixture.
    """
    try:
        # Create aliases for teams
        home_team = Team.__table__.alias("home_team")
        away_team = Team.__table__.alias("away_team")

        # Build query for single fixture
        query = select(
            Fixture,
            League.name.label("league_name"),
            home_team.c.name.label("home_team_name"),
            home_team.c.logo.label("home_team_logo"),
            away_team.c.name.label("away_team_name"),
            away_team.c.logo.label("away_team_logo"),
            Venue.name.label("venue_name"),
            Venue.city.label("venue_city")
        ).select_from(
            Fixture
            .join(League, Fixture.league_id == League.id)
            .join(home_team, Fixture.home_team_id == home_team.c.id)
            .join(away_team, Fixture.away_team_id == away_team.c.id)
            .outerjoin(Venue, Fixture.venue_id == Venue.id)
        ).where(Fixture.id == fixture_id)
        
        result = await db.execute(query)
        row = result.first()
        
        if not row:
            raise HTTPException(status_code=404, detail="Fixture not found")
        
        return format_fixture_response(row)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fixture {fixture_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/today/live")
async def get_today_live_fixtures(
    db: AsyncSession = Depends(get_db_session),
    user: Optional[Dict] = Depends(get_optional_user),
    rate_limit: None = Depends(api_rate_limit)
):
    """
    Get today's live fixtures.
    
    Returns fixtures that are currently live or scheduled for today.
    """
    try:
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        filters = FixtureFilters(
            date_from=today,
            date_to=today
        )
        
        query = build_fixture_query(filters)
        
        # Filter for live or upcoming matches
        query = query.where(
            Fixture.status_short.in_(['NS', '1H', '2H', 'HT', 'ET', 'BT', 'P'])
        ).order_by(Fixture.date)
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        fixtures = [format_fixture_response(row) for row in rows]
        
        return {
            "date": today.isoformat(),
            "fixtures": fixtures,
            "total": len(fixtures)
        }
        
    except Exception as e:
        logger.error(f"Error fetching today's live fixtures: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# FIXTURE DETAIL ENDPOINTS
# =============================================================================

@router.get("/{fixture_id}/statistics")
async def get_fixture_statistics(
    fixture_id: int,
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    db: AsyncSession = Depends(get_db_session),
    user: Optional[Dict] = Depends(get_optional_user),
    rate_limit: None = Depends(api_rate_limit)
):
    """
    Get fixture statistics.

    Returns detailed match statistics including shots, passes, possession, cards, etc.
    """
    try:
        # Verify fixture exists
        fixture_query = select(Fixture).where(Fixture.id == fixture_id)
        result = await db.execute(fixture_query)
        fixture = result.scalar_one_or_none()

        if not fixture:
            raise HTTPException(status_code=404, detail="Fixture not found")

        # Get statistics from API Football
        stats_service = FixtureStatisticsService()

        if team_id:
            # Get specific team statistics
            team_stats = stats_service.get_team_statistics(fixture_id, team_id)
            if not team_stats:
                return {"message": "No statistics found for this team", "data": None}
            return {"data": team_stats}
        else:
            # Get all statistics
            all_stats = stats_service.get_all_statistics(fixture_id)
            return {"data": all_stats}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fixture statistics {fixture_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{fixture_id}/lineups")
async def get_fixture_lineups(
    fixture_id: int,
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    db: AsyncSession = Depends(get_db_session),
    user: Optional[Dict] = Depends(get_optional_user),
    rate_limit: None = Depends(api_rate_limit)
):
    """
    Get fixture lineups.

    Returns team lineups including starting XI, substitutes, formation, and coach.
    """
    try:
        # Verify fixture exists
        fixture_query = select(Fixture).where(Fixture.id == fixture_id)
        result = await db.execute(fixture_query)
        fixture = result.scalar_one_or_none()

        if not fixture:
            raise HTTPException(status_code=404, detail="Fixture not found")

        # Get lineups from API Football
        lineups_service = FixtureLineupsService()

        if team_id:
            # Get specific team lineup
            team_lineup = lineups_service.get_team_lineup(fixture_id, team_id)
            if not team_lineup:
                return {"message": "No lineup found for this team", "data": None}
            return {"data": team_lineup}
        else:
            # Get all lineups
            all_lineups = lineups_service.get_all_lineups(fixture_id)
            return {"data": all_lineups}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fixture lineups {fixture_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{fixture_id}/events")
async def get_fixture_events(
    fixture_id: int,
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type (Goal, Card, subst, Var)"),
    db: AsyncSession = Depends(get_db_session),
    user: Optional[Dict] = Depends(get_optional_user),
    rate_limit: None = Depends(api_rate_limit)
):
    """
    Get fixture events.

    Returns match events including goals, cards, substitutions, and VAR decisions.
    """
    try:
        # Verify fixture exists
        fixture_query = select(Fixture).where(Fixture.id == fixture_id)
        result = await db.execute(fixture_query)
        fixture = result.scalar_one_or_none()

        if not fixture:
            raise HTTPException(status_code=404, detail="Fixture not found")

        # Get events from API Football
        events_service = FixtureEventsService()

        if event_type == "Goal":
            events = events_service.get_goals(fixture_id, team=team_id)
        elif event_type == "Card":
            events = events_service.get_cards(fixture_id, team=team_id)
        elif event_type == "subst":
            events = events_service.get_substitutions(fixture_id, team=team_id)
        elif event_type == "Var":
            events = events_service.get_var_events(fixture_id, team=team_id)
        else:
            # Get all events
            if team_id:
                result = events_service.get_fixture_events(fixture_id, team=team_id)
                events = result.get('response', [])
            else:
                events = events_service.get_all_events(fixture_id)

        return {"data": events}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fixture events {fixture_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{fixture_id}/h2h")
async def get_fixture_h2h(
    fixture_id: int,
    last: Optional[int] = Query(5, description="Number of recent matches to return"),
    db: AsyncSession = Depends(get_db_session),
    user: Optional[Dict] = Depends(get_optional_user),
    rate_limit: None = Depends(api_rate_limit)
):
    """
    Get fixture head-to-head data.

    Returns historical matches between the two teams.
    """
    try:
        # Get fixture to extract team IDs
        fixture_query = select(Fixture).where(Fixture.id == fixture_id)
        result = await db.execute(fixture_query)
        fixture = result.scalar_one_or_none()

        if not fixture:
            raise HTTPException(status_code=404, detail="Fixture not found")

        # Get H2H data from API Football
        h2h_service = FixtureH2HService()

        # Get recent matches between teams
        recent_matches = h2h_service.get_recent_h2h_matches(
            fixture.home_team_id,
            fixture.away_team_id,
            count=last
        )

        # Get H2H statistics
        h2h_stats = h2h_service.get_h2h_statistics(
            fixture.home_team_id,
            fixture.away_team_id
        )

        return {
            "data": {
                "recent_matches": recent_matches,
                "statistics": h2h_stats,
                "home_team_id": fixture.home_team_id,
                "away_team_id": fixture.away_team_id
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fixture H2H {fixture_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{fixture_id}/players")
async def get_fixture_player_statistics(
    fixture_id: int,
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    db: AsyncSession = Depends(get_db_session),
    user: Optional[Dict] = Depends(get_optional_user),
    rate_limit: None = Depends(api_rate_limit)
):
    """
    Get fixture player statistics.

    Returns detailed player performance statistics for the match.
    """
    try:
        # Verify fixture exists
        fixture_query = select(Fixture).where(Fixture.id == fixture_id)
        result = await db.execute(fixture_query)
        fixture = result.scalar_one_or_none()

        if not fixture:
            raise HTTPException(status_code=404, detail="Fixture not found")

        # Get player statistics from API Football
        player_stats_service = FixturePlayerStatisticsService()

        if team_id:
            # Get specific team player statistics
            team_stats = player_stats_service.get_team_player_stats(fixture_id, team_id)
            if not team_stats:
                return {"message": "No player statistics found for this team", "data": None}
            return {"data": team_stats}
        else:
            # Get all player statistics
            all_stats = player_stats_service.get_all_player_stats(fixture_id)

            # Also get top performers for quick access
            top_players = player_stats_service.get_top_rated_players(fixture_id, count=5)
            goal_scorers = player_stats_service.get_goal_scorers(fixture_id)
            assist_providers = player_stats_service.get_assist_providers(fixture_id)
            carded_players = player_stats_service.get_carded_players(fixture_id)

            return {
                "data": {
                    "teams": all_stats,
                    "highlights": {
                        "top_rated": top_players,
                        "goal_scorers": goal_scorers,
                        "assist_providers": assist_providers,
                        "yellow_cards": carded_players.get('yellow', []),
                        "red_cards": carded_players.get('red', [])
                    }
                }
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fixture player statistics {fixture_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
