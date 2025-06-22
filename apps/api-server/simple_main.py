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
        print(f"✓ Loaded environment variables from {env_path}")
    else:
        print(f"⚠ .env file not found at {env_path}")
except ImportError:
    print("⚠ python-dotenv not installed, using system environment variables")

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

# Initialize API services
try:
    fixtures_service = FixturesService()
    odds_service = OddsLiveService()
    events_service = FixtureEventsService()
    logger.info("✓ Real API services initialized successfully")
except Exception as e:
    logger.warning(f"⚠ Failed to initialize real API services: {e}")
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
    live: str = None
):
    """Get fixtures with optional filtering using real API."""
    try:
        if fixtures_service:
            # Use real API
            params = {}
            if league_id:
                params['league'] = league_id
            if season_year:
                params['season'] = season_year
            if status:
                params['status'] = status
            if date:
                params['date'] = date
            if live:
                params['live'] = live

            logger.info(f"Fetching fixtures with params: {params}")
            result = fixtures_service.get_fixtures(**params)

            if result and 'response' in result:
                fixtures = result['response']
                total = len(fixtures)

                # Apply pagination
                start = (page - 1) * per_page
                end = start + per_page
                fixtures_page = fixtures[start:end]

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

@app.get("/api/v1/fixtures/{fixture_id}")
async def get_fixture(fixture_id: int):
    """Get a specific fixture by ID using real API."""
    try:
        if fixtures_service:
            logger.info(f"Fetching fixture {fixture_id} from real API")
            result = fixtures_service.get_fixtures(fixture_id=fixture_id)

            if result and 'response' in result and result['response']:
                return result['response'][0]
            else:
                logger.warning(f"No fixture found for ID {fixture_id}")
                raise HTTPException(status_code=404, detail="Fixture not found")
        else:
            raise HTTPException(status_code=503, detail="Fixtures service unavailable")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fixture {fixture_id}: {e}")
        raise HTTPException(status_code=503, detail="External API service unavailable")

@app.get("/api/v1/fixtures/today/live")
async def get_today_live_fixtures():
    """Get today's live fixtures using real API."""
    try:
        if fixtures_service:
            # Get live fixtures from real API
            logger.info("Fetching live fixtures from real API")
            result = fixtures_service.get_live_fixtures()

            if result:
                return {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "fixtures": result,
                    "total": len(result),
                    "source": "real_api"
                }
            else:
                logger.warning("No live fixtures received from API")

    except Exception as e:
        logger.error(f"Error fetching live fixtures: {e}")
        raise HTTPException(status_code=503, detail="External API service unavailable")

# Live data endpoints
@app.get("/api/v1/live/odds/{fixture_id}")
async def get_live_odds(fixture_id: int):
    """Get live odds for a fixture using real API."""
    try:
        if odds_service:
            # Get live odds from real API
            logger.info(f"Fetching live odds for fixture {fixture_id}")
            result = odds_service.get_fixture_live_odds(fixture_id)

            if result:
                return {
                    "fixture_id": fixture_id,
                    "fixture": result.get('fixture', {}),
                    "odds": result.get('odds', []),
                    "timestamp": datetime.now().isoformat() + "Z",
                    "source": "real_api"
                }
            else:
                logger.warning(f"No live odds found for fixture {fixture_id}")

    except Exception as e:
        logger.error(f"Error fetching live odds for fixture {fixture_id}: {e}")
        raise HTTPException(status_code=503, detail="External API service unavailable")

@app.get("/api/v1/live/events/{fixture_id}")
async def get_live_events(fixture_id: int):
    """Get live events for a fixture using real API."""
    try:
        if events_service:
            logger.info(f"Fetching live events for fixture {fixture_id}")
            result = events_service.get_fixture_events(fixture_id)

            if result:
                return {
                    "fixture_id": fixture_id,
                    "events": result.get('response', []),
                    "timestamp": datetime.now().isoformat() + "Z",
                    "source": "real_api"
                }
            else:
                logger.warning(f"No events found for fixture {fixture_id}")
                return {
                    "fixture_id": fixture_id,
                    "events": [],
                    "timestamp": datetime.now().isoformat() + "Z",
                    "source": "real_api"
                }
        else:
            raise HTTPException(status_code=503, detail="Events service unavailable")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching events for fixture {fixture_id}: {e}")
        raise HTTPException(status_code=503, detail="External API service unavailable")

# Plugin endpoints
@app.get("/api/v1/plugins")
async def get_plugins():
    """Get available API wrapper plugins."""
    return {
        "plugins": [
            {
                "name": "fixtures_service",
                "description": "Match fixtures API wrapper",
                "status": "healthy",
                "endpoint": "fixtures"
            },
            {
                "name": "live_odds_service",
                "description": "Real-time odds API wrapper",
                "status": "healthy",
                "endpoint": "odds"
            },
            {
                "name": "live_events_service",
                "description": "Match events API wrapper",
                "status": "healthy",
                "endpoint": "events"
            }
        ]
    }

# WebSocket endpoints
@app.websocket("/ws/live/general")
async def websocket_live_general(websocket: WebSocket):
    """General live data WebSocket endpoint."""
    await manager.connect(websocket)

    try:
        # Send initial connection message
        await manager.send_personal_message(json.dumps({
            "type": "connection_established",
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to live data feed"
        }), websocket)

        while True:
            try:
                # Wait for client messages
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle different message types
                if message.get("type") == "ping":
                    await manager.send_personal_message(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }), websocket)

                elif message.get("type") == "subscribe":
                    fixture_id = message.get("fixture_id")
                    if fixture_id:
                        # Add to fixture-specific connections
                        if fixture_id not in manager.fixture_connections:
                            manager.fixture_connections[fixture_id] = []
                        if websocket not in manager.fixture_connections[fixture_id]:
                            manager.fixture_connections[fixture_id].append(websocket)

                        await manager.send_personal_message(json.dumps({
                            "type": "subscription_confirmed",
                            "fixture_id": fixture_id,
                            "timestamp": datetime.now().isoformat()
                        }), websocket)

                elif message.get("type") == "unsubscribe":
                    fixture_id = message.get("fixture_id")
                    if fixture_id and fixture_id in manager.fixture_connections:
                        if websocket in manager.fixture_connections[fixture_id]:
                            manager.fixture_connections[fixture_id].remove(websocket)

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await manager.send_personal_message(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }), websocket)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)

@app.websocket("/ws/live/{fixture_id}")
async def websocket_live_fixture(websocket: WebSocket, fixture_id: int):
    """Fixture-specific live data WebSocket endpoint."""
    await manager.connect(websocket, fixture_id)

    try:
        # Send initial connection message
        await manager.send_personal_message(json.dumps({
            "type": "connection_established",
            "fixture_id": fixture_id,
            "timestamp": datetime.now().isoformat(),
            "message": f"Connected to live data for fixture {fixture_id}"
        }), websocket)

        while True:
            try:
                # Wait for client messages
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle ping/pong
                if message.get("type") == "ping":
                    await manager.send_personal_message(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }), websocket)

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await manager.send_personal_message(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }), websocket)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )

# Development server
if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', '8001'))  # Use custom port
    
    logger.info(f"Starting Footy-Brain API Server on {host}:{port}")
    
    uvicorn.run(
        "simple_main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
        access_log=True
    )
