#!/usr/bin/env python3
"""
Footy-Brain v5 Simple API Server
Simplified version for quick testing without complex dependencies.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[OK] Loaded environment variables from {env_path}")
    else:
        print(f"[WARN] .env file not found at {env_path}")
except ImportError:
    print("[WARN] python-dotenv not installed, using system environment variables")

# Third-party imports
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import asyncio

# Import real API services
from tools.fixtures_service import FixturesService
from tools.odds_live_service import OddsLiveService
from tools.fixture_events_service import FixtureEventsService
from tools.api_config import APIConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Simple WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.fixture_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, fixture_id: int = None):
        await websocket.accept()
        self.active_connections.append(websocket)

        if fixture_id:
            if fixture_id not in self.fixture_connections:
                self.fixture_connections[fixture_id] = []
            self.fixture_connections[fixture_id].append(websocket)

        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        # Remove from fixture connections
        for fixture_id, connections in self.fixture_connections.items():
            if websocket in connections:
                connections.remove(websocket)

        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass  # Connection might be closed

    async def send_to_fixture(self, fixture_id: int, message: str):
        if fixture_id in self.fixture_connections:
            for connection in self.fixture_connections[fixture_id]:
                try:
                    await connection.send_text(message)
                except:
                    pass  # Connection might be closed

manager = ConnectionManager()

def transform_fixture_data(fixture_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform API-Football response to match frontend Fixture interface.

    Args:
        fixture_data: Raw fixture data from API-Football

    Returns:
        Transformed fixture data matching frontend interface
    """
    fixture = fixture_data.get('fixture', {})
    teams = fixture_data.get('teams', {})
    goals = fixture_data.get('goals', {})
    league = fixture_data.get('league', {})

    return {
        # Basic fixture info
        "id": fixture.get('id'),
        "referee": fixture.get('referee'),
        "timezone": fixture.get('timezone'),
        "date": fixture.get('date'),
        "timestamp": fixture.get('timestamp'),

        # Status info
        "status_short": fixture.get('status', {}).get('short'),
        "status_long": fixture.get('status', {}).get('long'),
        "status_elapsed": fixture.get('status', {}).get('elapsed'),
        "status_extra": fixture.get('status', {}).get('extra'),

        # League info
        "league_id": league.get('id'),
        "league_name": league.get('name'),
        "season_year": league.get('season'),
        "round": league.get('round'),

        # Team info
        "home_team_id": teams.get('home', {}).get('id'),
        "home_team_name": teams.get('home', {}).get('name'),
        "home_team_logo": teams.get('home', {}).get('logo'),
        "away_team_id": teams.get('away', {}).get('id'),
        "away_team_name": teams.get('away', {}).get('name'),
        "away_team_logo": teams.get('away', {}).get('logo'),

        # Goals
        "home_goals": goals.get('home', 0) or 0,
        "away_goals": goals.get('away', 0) or 0,
        "home_goals_ht": fixture_data.get('score', {}).get('halftime', {}).get('home', 0) or 0,
        "away_goals_ht": fixture_data.get('score', {}).get('halftime', {}).get('away', 0) or 0,
        "home_goals_et": fixture_data.get('score', {}).get('extratime', {}).get('home', 0) or 0,
        "away_goals_et": fixture_data.get('score', {}).get('extratime', {}).get('away', 0) or 0,
        "home_goals_pen": fixture_data.get('score', {}).get('penalty', {}).get('home', 0) or 0,
        "away_goals_pen": fixture_data.get('score', {}).get('penalty', {}).get('away', 0) or 0,

        # Venue info
        "venue_id": fixture.get('venue', {}).get('id'),
        "venue_name": fixture.get('venue', {}).get('name'),
        "venue_city": fixture.get('venue', {}).get('city'),

        # Timestamps
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

# Initialize API services
try:
    fixtures_service = FixturesService()
    odds_service = OddsLiveService()
    events_service = FixtureEventsService()
    logger.info("[OK] Real API services initialized successfully")
except Exception as e:
    logger.warning(f"[WARN] Failed to initialize real API services: {e}")
    fixtures_service = None
    odds_service = None
    events_service = None

# Create FastAPI application
app = FastAPI(
    title="Footy-Brain API",
    description="Real-time football data ingestion and analysis platform",
    version="5.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8001",
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)



# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "5.0.0",
        "environment": "development",
        "timestamp": datetime.now().isoformat() + "Z",
        "services": {
            "api": "healthy",
            "fixtures_service": "healthy" if fixtures_service else "unavailable",
            "odds_service": "healthy" if odds_service else "unavailable",
            "events_service": "healthy" if events_service else "unavailable"
        }
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Footy-Brain API",
        "version": "5.0.0",
        "description": "Real-time football data ingestion and analysis platform",
        "docs_url": "/docs",
        "health_url": "/health",
        "endpoints": {
            "fixtures": "/api/v1/fixtures",
            "live": "/api/v1/fixtures/today/live",
            "health": "/health"
        }
    }

# Fixtures endpoints
@app.get("/api/v1/fixtures")
async def get_fixtures(
    page: int = 1,
    per_page: int = 20,
    league_id: int = None,
    season_year: int = None,
    status: str = None,
    date: str = None,
    from_date: str = None,
    to_date: str = None,
    next_matches: int = None,
    last_matches: int = None,
    live: str = None
):
    """Get fixtures with optional filtering using real API.

    Supports O3's recommended patterns:
    - date=YYYY-MM-DD: Specific day (all leagues, all seasons)
    - league + season + next=N: Next N matches for specific league/season
    - league + season + last=N: Last N matches for specific league/season
    - from_date + to_date: Date range
    - live=all: Live matches
    """
    try:
        if fixtures_service:
            # Build query parameters using O3's patterns
            params = {}

            # O3 Pattern 1: Specific date (no season needed - API provides season_year)
            if date:
                params['date'] = date
                logger.info(f"📅 Fetching fixtures for specific date: {date}")

            # O3 Pattern 2: Date range
            elif from_date and to_date:
                params['from'] = from_date
                params['to'] = to_date
                logger.info(f"📅 Fetching fixtures from {from_date} to {to_date}")

            # O3 Pattern 3: Live matches
            elif live:
                params['live'] = live
                logger.info(f"🔴 Fetching live fixtures")

            # O3 Pattern 4: League-specific with next/last
            else:
                if league_id:
                    params['league'] = league_id
                if season_year:
                    params['season'] = season_year
                if status:
                    params['status'] = status
                if next_matches:
                    params['next'] = next_matches
                    logger.info(f"⏭️ Fetching next {next_matches} matches")
                elif last_matches:
                    params['last'] = last_matches
                    logger.info(f"⏮️ Fetching last {last_matches} matches")

            logger.info(f"Fetching fixtures with params: {params}")
            result = fixtures_service.get_fixtures(**params)

            if result and 'response' in result:
                fixtures = result['response']
                total = len(fixtures)

                # Transform fixtures to match frontend interface
                transformed_fixtures = []
                for fixture_data in fixtures:
                    transformed = transform_fixture_data(fixture_data)
                    transformed_fixtures.append(transformed)

                # Apply pagination
                start = (page - 1) * per_page
                end = start + per_page
                fixtures_page = transformed_fixtures[start:end]

                return {
                    "fixtures": fixtures_page,
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                    "total_pages": (total + per_page - 1) // per_page,
                    "api_info": result.get('paging', {}),
                    "source": "real_api"
                }
            else:
                logger.warning("No fixtures data received from API")

    except Exception as e:
        logger.error(f"Error fetching real fixtures: {e}")
        raise HTTPException(status_code=503, detail="External API service unavailable")

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8001"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    logger.info(f"Starting Footy-Brain API server on {host}:{port}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Reload: {reload}")
    
    uvicorn.run(
        "simple_main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )