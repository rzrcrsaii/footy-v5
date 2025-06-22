"""
Footy-Brain v5 Live Data Router
REST API endpoints for real-time live match data (odds, events, stats).
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
import asyncpg
from pydantic import BaseModel, Field

from apps.api_server.deps import get_raw_db_connection, get_optional_user, api_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class LiveOddsResponse(BaseModel):
    """Live odds response model."""
    
    id: str
    fixture_id: int
    bookmaker_id: int
    bookmaker_name: Optional[str]
    bet_market_id: int
    bet_market_name: Optional[str]
    bet_value: str
    odd_value: float
    timestamp: datetime
    match_minute: Optional[int]


class LiveEventResponse(BaseModel):
    """Live event response model."""
    
    id: str
    fixture_id: int
    event_type: str
    event_detail: Optional[str]
    event_comments: Optional[str]
    timestamp: datetime
    match_minute: Optional[int]
    match_minute_extra: Optional[int]
    team_id: Optional[int]
    team_name: Optional[str]
    player_id: Optional[int]
    player_name: Optional[str]
    assist_player_id: Optional[int]
    assist_player_name: Optional[str]


class LiveStatsResponse(BaseModel):
    """Live stats response model."""
    
    id: str
    fixture_id: int
    team_id: int
    team_name: Optional[str]
    timestamp: datetime
    match_minute: Optional[int]
    
    # Statistics
    shots_on_goal: int
    shots_off_goal: int
    total_shots: int
    blocked_shots: int
    shots_inside_box: int
    shots_outside_box: int
    fouls: int
    corner_kicks: int
    offsides: int
    ball_possession: int
    yellow_cards: int
    red_cards: int
    goalkeeper_saves: int
    total_passes: int
    passes_accurate: int
    passes_percentage: int


class LiveMatchSummary(BaseModel):
    """Live match summary response."""
    
    fixture_id: int
    home_team_id: int
    home_team_name: str
    away_team_id: int
    away_team_name: str
    status_short: str
    status_elapsed: Optional[int]
    home_goals: int
    away_goals: int
    
    # Latest odds (1X2)
    home_win_odd: Optional[float]
    draw_odd: Optional[float]
    away_win_odd: Optional[float]
    
    # Recent events count
    recent_events_count: int
    last_event_time: Optional[datetime]
    
    # Live stats summary
    home_possession: Optional[int]
    away_possession: Optional[int]
    home_shots: Optional[int]
    away_shots: Optional[int]


# =============================================================================
# API ENDPOINTS
# =============================================================================

@router.get("/{fixture_id}/odds", response_model=List[LiveOddsResponse])
async def get_live_odds(
    fixture_id: int,
    market_id: Optional[int] = Query(None, description="Filter by bet market ID"),
    bookmaker_id: Optional[int] = Query(None, description="Filter by bookmaker ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    minutes_back: int = Query(30, ge=1, le=180, description="Minutes of history to fetch"),
    db: asyncpg.Connection = Depends(get_raw_db_connection),
    user: Optional[Dict] = Depends(get_optional_user),
    rate_limit: None = Depends(api_rate_limit)
):
    """
    Get live odds for a specific fixture.
    
    Returns real-time odds data with optional filtering by market and bookmaker.
    """
    try:
        # Build query conditions
        conditions = ["lot.fixture_id = $1"]
        params = [fixture_id]
        param_count = 1
        
        if market_id:
            param_count += 1
            conditions.append(f"lot.bet_market_id = ${param_count}")
            params.append(market_id)
        
        if bookmaker_id:
            param_count += 1
            conditions.append(f"lot.bookmaker_id = ${param_count}")
            params.append(bookmaker_id)
        
        # Add time filter
        param_count += 1
        conditions.append(f"lot.timestamp >= NOW() - INTERVAL '{minutes_back} minutes'")
        
        query = f"""
            SELECT 
                lot.id,
                lot.fixture_id,
                lot.bookmaker_id,
                b.name as bookmaker_name,
                lot.bet_market_id,
                bdm.name as bet_market_name,
                lot.bet_value,
                lot.odd_value,
                lot.timestamp,
                lot.match_minute
            FROM live_odds_tick lot
            LEFT JOIN bookmaker b ON lot.bookmaker_id = b.id
            LEFT JOIN bet_def_market bdm ON lot.bet_market_id = bdm.id
            WHERE {' AND '.join(conditions)}
            ORDER BY lot.timestamp DESC
            LIMIT ${param_count + 1}
        """
        params.append(limit)
        
        rows = await db.fetch(query, *params)
        
        odds = []
        for row in rows:
            odds.append(LiveOddsResponse(
                id=str(row['id']),
                fixture_id=row['fixture_id'],
                bookmaker_id=row['bookmaker_id'],
                bookmaker_name=row['bookmaker_name'],
                bet_market_id=row['bet_market_id'],
                bet_market_name=row['bet_market_name'],
                bet_value=row['bet_value'],
                odd_value=float(row['odd_value']),
                timestamp=row['timestamp'],
                match_minute=row['match_minute']
            ))
        
        return odds
        
    except Exception as e:
        logger.error(f"Error fetching live odds for fixture {fixture_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{fixture_id}/events", response_model=List[LiveEventResponse])
async def get_live_events(
    fixture_id: int,
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    minutes_back: int = Query(90, ge=1, le=180, description="Minutes of history to fetch"),
    db: asyncpg.Connection = Depends(get_raw_db_connection),
    user: Optional[Dict] = Depends(get_optional_user),
    rate_limit: None = Depends(api_rate_limit)
):
    """
    Get live events for a specific fixture.
    
    Returns real-time match events like goals, cards, substitutions.
    """
    try:
        # Build query conditions
        conditions = ["let.fixture_id = $1"]
        params = [fixture_id]
        param_count = 1
        
        if event_type:
            param_count += 1
            conditions.append(f"let.event_type = ${param_count}")
            params.append(event_type)
        
        if team_id:
            param_count += 1
            conditions.append(f"let.team_id = ${param_count}")
            params.append(team_id)
        
        # Add time filter
        param_count += 1
        conditions.append(f"let.timestamp >= NOW() - INTERVAL '{minutes_back} minutes'")
        
        query = f"""
            SELECT 
                let.id,
                let.fixture_id,
                let.event_type,
                let.event_detail,
                let.event_comments,
                let.timestamp,
                let.match_minute,
                let.match_minute_extra,
                let.team_id,
                t.name as team_name,
                let.player_id,
                p.name as player_name,
                let.assist_player_id,
                ap.name as assist_player_name
            FROM live_event_tick let
            LEFT JOIN team t ON let.team_id = t.id
            LEFT JOIN player p ON let.player_id = p.id
            LEFT JOIN player ap ON let.assist_player_id = ap.id
            WHERE {' AND '.join(conditions)}
            ORDER BY let.timestamp DESC
            LIMIT ${param_count + 1}
        """
        params.append(limit)
        
        rows = await db.fetch(query, *params)
        
        events = []
        for row in rows:
            events.append(LiveEventResponse(
                id=str(row['id']),
                fixture_id=row['fixture_id'],
                event_type=row['event_type'],
                event_detail=row['event_detail'],
                event_comments=row['event_comments'],
                timestamp=row['timestamp'],
                match_minute=row['match_minute'],
                match_minute_extra=row['match_minute_extra'],
                team_id=row['team_id'],
                team_name=row['team_name'],
                player_id=row['player_id'],
                player_name=row['player_name'],
                assist_player_id=row['assist_player_id'],
                assist_player_name=row['assist_player_name']
            ))
        
        return events
        
    except Exception as e:
        logger.error(f"Error fetching live events for fixture {fixture_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{fixture_id}/stats", response_model=List[LiveStatsResponse])
async def get_live_stats(
    fixture_id: int,
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of records"),
    minutes_back: int = Query(30, ge=1, le=180, description="Minutes of history to fetch"),
    db: asyncpg.Connection = Depends(get_raw_db_connection),
    user: Optional[Dict] = Depends(get_optional_user),
    rate_limit: None = Depends(api_rate_limit)
):
    """
    Get live statistics for a specific fixture.
    
    Returns real-time match statistics like possession, shots, passes.
    """
    try:
        # Build query conditions
        conditions = ["lst.fixture_id = $1"]
        params = [fixture_id]
        param_count = 1
        
        if team_id:
            param_count += 1
            conditions.append(f"lst.team_id = ${param_count}")
            params.append(team_id)
        
        # Add time filter
        param_count += 1
        conditions.append(f"lst.timestamp >= NOW() - INTERVAL '{minutes_back} minutes'")
        
        query = f"""
            SELECT 
                lst.id,
                lst.fixture_id,
                lst.team_id,
                t.name as team_name,
                lst.timestamp,
                lst.match_minute,
                lst.shots_on_goal,
                lst.shots_off_goal,
                lst.total_shots,
                lst.blocked_shots,
                lst.shots_inside_box,
                lst.shots_outside_box,
                lst.fouls,
                lst.corner_kicks,
                lst.offsides,
                lst.ball_possession,
                lst.yellow_cards,
                lst.red_cards,
                lst.goalkeeper_saves,
                lst.total_passes,
                lst.passes_accurate,
                lst.passes_percentage
            FROM live_stats_tick lst
            LEFT JOIN team t ON lst.team_id = t.id
            WHERE {' AND '.join(conditions)}
            ORDER BY lst.timestamp DESC
            LIMIT ${param_count + 1}
        """
        params.append(limit)
        
        rows = await db.fetch(query, *params)
        
        stats = []
        for row in rows:
            stats.append(LiveStatsResponse(
                id=str(row['id']),
                fixture_id=row['fixture_id'],
                team_id=row['team_id'],
                team_name=row['team_name'],
                timestamp=row['timestamp'],
                match_minute=row['match_minute'],
                shots_on_goal=row['shots_on_goal'],
                shots_off_goal=row['shots_off_goal'],
                total_shots=row['total_shots'],
                blocked_shots=row['blocked_shots'],
                shots_inside_box=row['shots_inside_box'],
                shots_outside_box=row['shots_outside_box'],
                fouls=row['fouls'],
                corner_kicks=row['corner_kicks'],
                offsides=row['offsides'],
                ball_possession=row['ball_possession'],
                yellow_cards=row['yellow_cards'],
                red_cards=row['red_cards'],
                goalkeeper_saves=row['goalkeeper_saves'],
                total_passes=row['total_passes'],
                passes_accurate=row['passes_accurate'],
                passes_percentage=row['passes_percentage']
            ))
        
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching live stats for fixture {fixture_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{fixture_id}/summary", response_model=LiveMatchSummary)
async def get_live_match_summary(
    fixture_id: int,
    db: asyncpg.Connection = Depends(get_raw_db_connection),
    user: Optional[Dict] = Depends(get_optional_user),
    rate_limit: None = Depends(api_rate_limit)
):
    """
    Get live match summary with key information.
    
    Returns a comprehensive summary of the live match including scores, odds, and stats.
    """
    try:
        # Get fixture basic info
        fixture_query = """
            SELECT 
                f.id,
                f.home_team_id,
                ht.name as home_team_name,
                f.away_team_id,
                at.name as away_team_name,
                f.status_short,
                f.status_elapsed,
                f.home_goals,
                f.away_goals
            FROM fixture f
            JOIN team ht ON f.home_team_id = ht.id
            JOIN team at ON f.away_team_id = at.id
            WHERE f.id = $1
        """
        
        fixture_row = await db.fetchrow(fixture_query, fixture_id)
        
        if not fixture_row:
            raise HTTPException(status_code=404, detail="Fixture not found")
        
        # Get latest 1X2 odds
        odds_query = """
            SELECT 
                AVG(CASE WHEN bet_value = '1' THEN odd_value END) as home_win_odd,
                AVG(CASE WHEN bet_value = 'X' THEN odd_value END) as draw_odd,
                AVG(CASE WHEN bet_value = '2' THEN odd_value END) as away_win_odd
            FROM live_odds_tick
            WHERE fixture_id = $1 
            AND bet_market_id = 1  -- Match Winner market
            AND timestamp >= NOW() - INTERVAL '5 minutes'
        """
        
        odds_row = await db.fetchrow(odds_query, fixture_id)
        
        # Get recent events count
        events_query = """
            SELECT 
                COUNT(*) as recent_events_count,
                MAX(timestamp) as last_event_time
            FROM live_event_tick
            WHERE fixture_id = $1 
            AND timestamp >= NOW() - INTERVAL '10 minutes'
        """
        
        events_row = await db.fetchrow(events_query, fixture_id)
        
        # Get latest possession stats
        stats_query = """
            SELECT 
                team_id,
                ball_possession,
                total_shots
            FROM live_stats_tick
            WHERE fixture_id = $1
            AND timestamp >= NOW() - INTERVAL '5 minutes'
            ORDER BY timestamp DESC
            LIMIT 2
        """
        
        stats_rows = await db.fetch(stats_query, fixture_id)
        
        # Process stats
        home_possession = None
        away_possession = None
        home_shots = None
        away_shots = None
        
        for stat in stats_rows:
            if stat['team_id'] == fixture_row['home_team_id']:
                home_possession = stat['ball_possession']
                home_shots = stat['total_shots']
            elif stat['team_id'] == fixture_row['away_team_id']:
                away_possession = stat['ball_possession']
                away_shots = stat['total_shots']
        
        return LiveMatchSummary(
            fixture_id=fixture_row['id'],
            home_team_id=fixture_row['home_team_id'],
            home_team_name=fixture_row['home_team_name'],
            away_team_id=fixture_row['away_team_id'],
            away_team_name=fixture_row['away_team_name'],
            status_short=fixture_row['status_short'],
            status_elapsed=fixture_row['status_elapsed'],
            home_goals=fixture_row['home_goals'],
            away_goals=fixture_row['away_goals'],
            home_win_odd=float(odds_row['home_win_odd']) if odds_row['home_win_odd'] else None,
            draw_odd=float(odds_row['draw_odd']) if odds_row['draw_odd'] else None,
            away_win_odd=float(odds_row['away_win_odd']) if odds_row['away_win_odd'] else None,
            recent_events_count=events_row['recent_events_count'],
            last_event_time=events_row['last_event_time'],
            home_possession=home_possession,
            away_possession=away_possession,
            home_shots=home_shots,
            away_shots=away_shots
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching live match summary for fixture {fixture_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
