"""
Footy-Brain v5 Prematch Router
REST API endpoints for pre-match odds snapshots and analysis.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
import asyncpg
from pydantic import BaseModel

from apps.api_server.deps import get_raw_db_connection, get_optional_user, api_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class PrematchOddsResponse(BaseModel):
    """Prematch odds response model."""
    
    id: str
    fixture_id: int
    bookmaker_id: int
    bookmaker_name: Optional[str]
    bet_market_id: int
    bet_market_name: Optional[str]
    bet_value: str
    odd_value: float
    snapshot_time: datetime
    hours_before_match: Optional[int]


class OddsMovementResponse(BaseModel):
    """Odds movement analysis response."""
    
    fixture_id: int
    bet_market_id: int
    bet_value: str
    
    # Movement data
    opening_odd: Optional[float]
    current_odd: Optional[float]
    highest_odd: Optional[float]
    lowest_odd: Optional[float]
    
    # Change metrics
    absolute_change: Optional[float]
    percentage_change: Optional[float]
    
    # Timing
    first_snapshot: Optional[datetime]
    last_snapshot: Optional[datetime]
    snapshots_count: int


# =============================================================================
# API ENDPOINTS
# =============================================================================

@router.get("/{fixture_id}/odds", response_model=List[PrematchOddsResponse])
async def get_prematch_odds(
    fixture_id: int,
    market_id: Optional[int] = Query(None, description="Filter by bet market ID"),
    bookmaker_id: Optional[int] = Query(None, description="Filter by bookmaker ID"),
    hours_before: Optional[int] = Query(None, description="Filter by hours before match"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: asyncpg.Connection = Depends(get_raw_db_connection),
    user: Optional[Dict] = Depends(get_optional_user),
    rate_limit: None = Depends(api_rate_limit)
):
    """
    Get prematch odds for a specific fixture.
    
    Returns historical prematch odds snapshots with optional filtering.
    """
    try:
        # Build query conditions
        conditions = ["po.fixture_id = $1"]
        params = [fixture_id]
        param_count = 1
        
        if market_id:
            param_count += 1
            conditions.append(f"po.bet_market_id = ${param_count}")
            params.append(market_id)
        
        if bookmaker_id:
            param_count += 1
            conditions.append(f"po.bookmaker_id = ${param_count}")
            params.append(bookmaker_id)
        
        if hours_before:
            param_count += 1
            conditions.append(f"po.hours_before_match = ${param_count}")
            params.append(hours_before)
        
        query = f"""
            SELECT 
                po.id,
                po.fixture_id,
                po.bookmaker_id,
                b.name as bookmaker_name,
                po.bet_market_id,
                bdm.name as bet_market_name,
                po.bet_value,
                po.odd_value,
                po.snapshot_time,
                po.hours_before_match
            FROM prematch_odds po
            LEFT JOIN bookmaker b ON po.bookmaker_id = b.id
            LEFT JOIN bet_def_market bdm ON po.bet_market_id = bdm.id
            WHERE {' AND '.join(conditions)}
            ORDER BY po.snapshot_time DESC
            LIMIT ${param_count + 1}
        """
        params.append(limit)
        
        rows = await db.fetch(query, *params)
        
        odds = []
        for row in rows:
            odds.append(PrematchOddsResponse(
                id=str(row['id']),
                fixture_id=row['fixture_id'],
                bookmaker_id=row['bookmaker_id'],
                bookmaker_name=row['bookmaker_name'],
                bet_market_id=row['bet_market_id'],
                bet_market_name=row['bet_market_name'],
                bet_value=row['bet_value'],
                odd_value=float(row['odd_value']),
                snapshot_time=row['snapshot_time'],
                hours_before_match=row['hours_before_match']
            ))
        
        return odds
        
    except Exception as e:
        logger.error(f"Error fetching prematch odds for fixture {fixture_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{fixture_id}/movement", response_model=List[OddsMovementResponse])
async def get_odds_movement(
    fixture_id: int,
    market_id: Optional[int] = Query(None, description="Filter by bet market ID"),
    db: asyncpg.Connection = Depends(get_raw_db_connection),
    user: Optional[Dict] = Depends(get_optional_user),
    rate_limit: None = Depends(api_rate_limit)
):
    """
    Get odds movement analysis for a fixture.
    
    Returns analysis of how odds have changed over time for each bet value.
    """
    try:
        # Build query conditions
        conditions = ["po.fixture_id = $1"]
        params = [fixture_id]
        param_count = 1
        
        if market_id:
            param_count += 1
            conditions.append(f"po.bet_market_id = ${param_count}")
            params.append(market_id)
        
        query = f"""
            SELECT 
                po.fixture_id,
                po.bet_market_id,
                po.bet_value,
                
                -- Opening and current odds
                FIRST_VALUE(AVG(po.odd_value)) OVER (
                    PARTITION BY po.bet_market_id, po.bet_value 
                    ORDER BY po.snapshot_time ASC 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                ) as opening_odd,
                
                LAST_VALUE(AVG(po.odd_value)) OVER (
                    PARTITION BY po.bet_market_id, po.bet_value 
                    ORDER BY po.snapshot_time ASC 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                ) as current_odd,
                
                -- Min/Max odds
                MAX(po.odd_value) OVER (
                    PARTITION BY po.bet_market_id, po.bet_value
                ) as highest_odd,
                
                MIN(po.odd_value) OVER (
                    PARTITION BY po.bet_market_id, po.bet_value
                ) as lowest_odd,
                
                -- Timing
                MIN(po.snapshot_time) OVER (
                    PARTITION BY po.bet_market_id, po.bet_value
                ) as first_snapshot,
                
                MAX(po.snapshot_time) OVER (
                    PARTITION BY po.bet_market_id, po.bet_value
                ) as last_snapshot,
                
                COUNT(*) OVER (
                    PARTITION BY po.bet_market_id, po.bet_value
                ) as snapshots_count
                
            FROM prematch_odds po
            WHERE {' AND '.join(conditions)}
            GROUP BY po.fixture_id, po.bet_market_id, po.bet_value, po.odd_value, po.snapshot_time
        """
        
        rows = await db.fetch(query, *params)
        
        # Process results to get unique bet values
        movement_data = {}
        
        for row in rows:
            key = (row['bet_market_id'], row['bet_value'])
            
            if key not in movement_data:
                opening_odd = float(row['opening_odd']) if row['opening_odd'] else None
                current_odd = float(row['current_odd']) if row['current_odd'] else None
                
                # Calculate changes
                absolute_change = None
                percentage_change = None
                
                if opening_odd and current_odd:
                    absolute_change = current_odd - opening_odd
                    percentage_change = (absolute_change / opening_odd) * 100
                
                movement_data[key] = OddsMovementResponse(
                    fixture_id=row['fixture_id'],
                    bet_market_id=row['bet_market_id'],
                    bet_value=row['bet_value'],
                    opening_odd=opening_odd,
                    current_odd=current_odd,
                    highest_odd=float(row['highest_odd']) if row['highest_odd'] else None,
                    lowest_odd=float(row['lowest_odd']) if row['lowest_odd'] else None,
                    absolute_change=absolute_change,
                    percentage_change=percentage_change,
                    first_snapshot=row['first_snapshot'],
                    last_snapshot=row['last_snapshot'],
                    snapshots_count=row['snapshots_count']
                )
        
        return list(movement_data.values())
        
    except Exception as e:
        logger.error(f"Error fetching odds movement for fixture {fixture_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/upcoming")
async def get_upcoming_matches_with_odds(
    hours_ahead: int = Query(24, ge=1, le=168, description="Hours ahead to look"),
    min_bookmakers: int = Query(3, ge=1, le=10, description="Minimum bookmakers required"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of matches"),
    db: asyncpg.Connection = Depends(get_raw_db_connection),
    user: Optional[Dict] = Depends(get_optional_user),
    rate_limit: None = Depends(api_rate_limit)
):
    """
    Get upcoming matches with available prematch odds.
    
    Returns fixtures that have prematch odds available from multiple bookmakers.
    """
    try:
        query = """
            SELECT 
                f.id as fixture_id,
                f.date,
                f.league_id,
                l.name as league_name,
                f.home_team_id,
                ht.name as home_team_name,
                f.away_team_id,
                at.name as away_team_name,
                f.round,
                
                -- Odds summary
                COUNT(DISTINCT po.bookmaker_id) as bookmaker_count,
                AVG(CASE WHEN po.bet_value = '1' THEN po.odd_value END) as avg_home_odd,
                AVG(CASE WHEN po.bet_value = 'X' THEN po.odd_value END) as avg_draw_odd,
                AVG(CASE WHEN po.bet_value = '2' THEN po.odd_value END) as avg_away_odd,
                
                MAX(po.snapshot_time) as latest_odds_time
                
            FROM fixture f
            JOIN league l ON f.league_id = l.id
            JOIN team ht ON f.home_team_id = ht.id
            JOIN team at ON f.away_team_id = at.id
            LEFT JOIN prematch_odds po ON f.id = po.fixture_id 
                AND po.bet_market_id = 1  -- Match Winner market
                AND po.snapshot_time >= NOW() - INTERVAL '24 hours'
            
            WHERE f.status_short = 'NS'
            AND f.date >= NOW()
            AND f.date <= NOW() + INTERVAL '%s hours'
            
            GROUP BY f.id, f.date, f.league_id, l.name, f.home_team_id, ht.name, 
                     f.away_team_id, at.name, f.round
            
            HAVING COUNT(DISTINCT po.bookmaker_id) >= $2
            
            ORDER BY f.date ASC
            LIMIT $3
        """
        
        rows = await db.fetch(query % hours_ahead, min_bookmakers, limit)
        
        matches = []
        for row in rows:
            matches.append({
                "fixture_id": row['fixture_id'],
                "date": row['date'].isoformat(),
                "league_id": row['league_id'],
                "league_name": row['league_name'],
                "home_team_id": row['home_team_id'],
                "home_team_name": row['home_team_name'],
                "away_team_id": row['away_team_id'],
                "away_team_name": row['away_team_name'],
                "round": row['round'],
                "bookmaker_count": row['bookmaker_count'],
                "avg_home_odd": float(row['avg_home_odd']) if row['avg_home_odd'] else None,
                "avg_draw_odd": float(row['avg_draw_odd']) if row['avg_draw_odd'] else None,
                "avg_away_odd": float(row['avg_away_odd']) if row['avg_away_odd'] else None,
                "latest_odds_time": row['latest_odds_time'].isoformat() if row['latest_odds_time'] else None
            })
        
        return {
            "matches": matches,
            "total": len(matches),
            "hours_ahead": hours_ahead,
            "min_bookmakers": min_bookmakers
        }
        
    except Exception as e:
        logger.error(f"Error fetching upcoming matches with odds: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
