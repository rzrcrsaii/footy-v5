"""
Footy-Brain v5 API Server
FastAPI-based REST API with WebSocket support for real-time football data.

This is the main entry point for the API server that:
1. Loads configuration from .env and YAML files
2. Initializes database connections and runs DDL scripts
3. Sets up plugin discovery for API wrappers
4. Configures Celery Beat schedules
5. Mounts routers and WebSocket endpoints
6. Adds JWT authentication and CORS
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

import uvicorn
import yaml
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from apps.api_server.db.init import initialize_database
from apps.api_server.deps import get_current_user, get_db_session
from apps.api_server.plugin_loader import discover_plugins, load_plugin_metadata
from apps.api_server.tasks import setup_celery_beat_schedules

# Import routers
from apps.api_server.routers import (
    fixtures,
    live,
    prematch,
    cronjobs,
    settings,
    plugins
)
from apps.api_server.realtime.websocket import websocket_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global configuration
app_config: Dict[str, Any] = {}
security = HTTPBearer()


def load_configuration() -> Dict[str, Any]:
    """Load configuration from environment variables and YAML files."""
    config = {}
    
    # Load environment variables
    config['environment'] = os.getenv('ENVIRONMENT', 'development')
    config['debug'] = os.getenv('DEBUG', 'false').lower() == 'true'
    config['api_host'] = os.getenv('API_HOST', '0.0.0.0')
    config['api_port'] = int(os.getenv('API_PORT', '8000'))
    
    # Database configuration
    config['database_url'] = os.getenv('DATABASE_URL', 
        'postgresql://footy:footy_secure_2024@localhost:5432/footy')
    config['redis_url'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Security
    config['jwt_secret'] = os.getenv('JWT_SECRET', 'footy_jwt_secret_2024')
    config['rapidapi_key'] = os.getenv('RAPIDAPI_KEY', '')
    
    # Load YAML configurations
    config_dir = project_root / 'config'
    
    try:
        # Load app.yml
        with open(config_dir / 'app.yml', 'r') as f:
            app_yml = yaml.safe_load(f)
            config['app'] = app_yml
            
        # Load leagues.yml
        with open(config_dir / 'leagues.yml', 'r') as f:
            leagues_yml = yaml.safe_load(f)
            config['leagues'] = leagues_yml
            
        # Load workers.yml
        with open(config_dir / 'workers.yml', 'r') as f:
            workers_yml = yaml.safe_load(f)
            config['workers'] = workers_yml
            
        logger.info("Configuration loaded successfully")
        
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration: {e}")
        raise
    
    return config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Footy-Brain API Server v5.0.0")
    
    try:
        # Load configuration
        global app_config
        app_config = load_configuration()
        app.state.config = app_config
        
        # Initialize database
        logger.info("Initializing database...")
        await initialize_database(app_config['database_url'])
        
        # Discover and load plugins
        logger.info("Discovering API wrapper plugins...")
        plugins_info = await discover_plugins()
        app.state.plugins = plugins_info
        logger.info(f"Discovered {len(plugins_info)} plugins")
        
        # Setup Celery Beat schedules
        if app_config['environment'] != 'testing':
            logger.info("Setting up Celery Beat schedules...")
            await setup_celery_beat_schedules(app_config['workers'])
        
        logger.info("API Server startup completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Footy-Brain API Server")


# Create FastAPI application
app = FastAPI(
    title="Footy-Brain API",
    description="Real-time football data ingestion and analysis platform",
    version="5.0.0",
    docs_url="/docs" if os.getenv('ENVIRONMENT') != 'production' else None,
    redoc_url="/redoc" if os.getenv('ENVIRONMENT') != 'production' else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        os.getenv('FRONTEND_URL', 'http://localhost:3000')
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure properly for production
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # TODO: Add database connectivity check
        # TODO: Add Redis connectivity check
        # TODO: Add external API connectivity check (optional)
        
        return {
            "status": "healthy",
            "version": "5.0.0",
            "environment": app_config.get('environment', 'unknown'),
            "timestamp": "2024-01-01T00:00:00Z"  # TODO: Use actual timestamp
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Footy-Brain API",
        "version": "5.0.0",
        "description": "Real-time football data ingestion and analysis platform",
        "docs_url": "/docs" if os.getenv('ENVIRONMENT') != 'production' else None,
        "health_url": "/health"
    }


# Authentication endpoint
@app.post("/auth/token")
async def login(credentials: dict):
    """
    Authenticate user and return JWT token.
    TODO: Implement proper authentication logic.
    """
    # TODO: Implement actual authentication
    raise HTTPException(status_code=501, detail="Authentication not implemented")


# Protected endpoint example
@app.get("/protected")
async def protected_endpoint(current_user: dict = Depends(get_current_user)):
    """Example of a protected endpoint requiring authentication."""
    return {"message": f"Hello {current_user.get('username', 'user')}!"}


# Mount routers
app.include_router(fixtures.router, prefix="/api/v1/fixtures", tags=["fixtures"])
app.include_router(live.router, prefix="/api/v1/live", tags=["live"])
app.include_router(prematch.router, prefix="/api/v1/prematch", tags=["prematch"])
app.include_router(cronjobs.router, prefix="/api/v1/cronjobs", tags=["cronjobs"])
app.include_router(settings.router, prefix="/api/v1/settings", tags=["settings"])
app.include_router(plugins.router, prefix="/api/v1/plugins", tags=["plugins"])

# Mount WebSocket router
app.include_router(websocket_router, prefix="/ws")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    if app_config.get('debug', False):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )
    
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


# Development server
if __name__ == "__main__":
    # Load configuration for development
    config = load_configuration()
    
    uvicorn.run(
        "main:app",
        host=config['api_host'],
        port=config['api_port'],
        reload=config.get('debug', False),
        log_level="info" if not config.get('debug') else "debug",
        access_log=True
    )
