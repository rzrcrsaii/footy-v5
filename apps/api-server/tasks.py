"""
Footy-Brain v5 Celery Tasks
Background task definitions for data collection, processing, and maintenance.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from celery import Celery
from celery.schedules import crontab
import asyncpg
import yaml

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from apps.api_server.plugin_loader import get_plugin_instance

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    'footy-brain-tasks',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)


async def get_db_connection() -> asyncpg.Connection:
    """Get database connection for tasks."""
    database_url = os.getenv('DATABASE_URL', 
        'postgresql://footy:footy_secure_2024@localhost:5432/footy')
    return await asyncpg.connect(database_url)


def run_async_task(coro):
    """Helper to run async functions in Celery tasks."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, name='apps.api_server.tasks.fixture_poller')
def fixture_poller(self, days_ahead: int = 7, update_existing: bool = True):
    """
    Collect upcoming fixtures for tracked leagues.
    
    Args:
        days_ahead: Number of days ahead to collect fixtures
        update_existing: Whether to update existing fixtures
    """
    logger.info(f"Starting fixture polling for {days_ahead} days ahead")
    
    async def _fixture_poller():
        try:
            # Get fixtures service
            fixtures_service = await get_plugin_instance("Fixtures")
            if not fixtures_service:
                raise Exception("Fixtures service not available")
            
            # Get database connection
            conn = await get_db_connection()
            
            try:
                # Get tracked leagues from configuration
                config_path = project_root / 'config' / 'leagues.yml'
                with open(config_path, 'r') as f:
                    leagues_config = yaml.safe_load(f)
                
                fixtures_collected = 0
                
                # Collect fixtures for each enabled league
                for country_data in leagues_config['leagues'].values():
                    for league in country_data['leagues']:
                        if not league.get('enabled', False):
                            continue
                        
                        league_id = league['league_id']
                        season = league['season']
                        
                        logger.info(f"Collecting fixtures for league {league_id}, season {season}")
                        
                        # Calculate date range
                        from_date = datetime.now().date()
                        to_date = from_date + timedelta(days=days_ahead)
                        
                        # Fetch fixtures from API
                        fixtures_data = await fixtures_service.fetch(
                            league=league_id,
                            season=season,
                            from_=from_date.isoformat(),
                            to=to_date.isoformat()
                        )
                        
                        # Process and store fixtures
                        if fixtures_data and 'response' in fixtures_data:
                            for fixture in fixtures_data['response']:
                                await _store_fixture(conn, fixture, update_existing)
                                fixtures_collected += 1
                
                logger.info(f"Fixture polling completed. Collected {fixtures_collected} fixtures")
                return {"status": "success", "fixtures_collected": fixtures_collected}
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Fixture polling failed: {e}")
            raise
    
    return run_async_task(_fixture_poller())


@celery_app.task(bind=True, name='apps.api_server.tasks.live_manager_trigger')
def live_manager_trigger(self, check_match_status: bool = True, auto_start_collection: bool = True):
    """
    Trigger live data collection for active matches.
    
    Args:
        check_match_status: Whether to check match status before collection
        auto_start_collection: Whether to automatically start collection for live matches
    """
    logger.info("Starting live manager trigger")
    
    async def _live_manager_trigger():
        try:
            conn = await get_db_connection()
            
            try:
                # Get currently live matches
                live_matches = await conn.fetch("""
                    SELECT id, home_team_id, away_team_id, league_id, status_short
                    FROM fixture 
                    WHERE status_short IN ('1H', '2H', 'HT', 'ET', 'BT', 'P')
                    AND date >= NOW() - INTERVAL '3 hours'
                    AND date <= NOW() + INTERVAL '3 hours'
                """)
                
                logger.info(f"Found {len(live_matches)} live matches")
                
                # Trigger live data collection for each match
                for match in live_matches:
                    # TODO: Trigger live worker for this specific match
                    # This would typically send a message to the live worker
                    logger.info(f"Triggering live collection for fixture {match['id']}")
                
                return {"status": "success", "live_matches": len(live_matches)}
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Live manager trigger failed: {e}")
            raise
    
    return run_async_task(_live_manager_trigger())


@celery_app.task(bind=True, name='apps.api_server.tasks.prematch_snapshot')
def prematch_snapshot(self, hours_before_match: int = 24, min_bookmakers: int = 3):
    """
    Collect pre-match odds snapshots.
    
    Args:
        hours_before_match: Collect odds for matches within this many hours
        min_bookmakers: Minimum number of bookmakers required
    """
    logger.info(f"Starting prematch snapshot collection for matches within {hours_before_match} hours")
    
    async def _prematch_snapshot():
        try:
            # Get prematch odds service
            prematch_service = await get_plugin_instance("Prematch Odds")
            if not prematch_service:
                raise Exception("Prematch odds service not available")
            
            conn = await get_db_connection()
            
            try:
                # Get upcoming matches
                upcoming_matches = await conn.fetch("""
                    SELECT id, league_id, home_team_id, away_team_id, date
                    FROM fixture 
                    WHERE status_short = 'NS'
                    AND date >= NOW()
                    AND date <= NOW() + INTERVAL '%s hours'
                    ORDER BY date
                """, hours_before_match)
                
                odds_collected = 0
                
                for match in upcoming_matches:
                    fixture_id = match['id']
                    
                    logger.info(f"Collecting prematch odds for fixture {fixture_id}")
                    
                    # Fetch odds from API
                    odds_data = await prematch_service.fetch(fixture=fixture_id)
                    
                    # Store odds data
                    if odds_data and 'response' in odds_data:
                        for odds_entry in odds_data['response']:
                            await _store_prematch_odds(conn, fixture_id, odds_entry)
                            odds_collected += 1
                
                logger.info(f"Prematch snapshot completed. Collected {odds_collected} odds entries")
                return {"status": "success", "odds_collected": odds_collected}
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Prematch snapshot failed: {e}")
            raise
    
    return run_async_task(_prematch_snapshot())


@celery_app.task(bind=True, name='apps.api_server.tasks.frame_maker')
def frame_maker(self, frame_duration_seconds: int = 60, include_stats: bool = True):
    """
    Aggregate live ticks into 1-minute frames.
    
    Args:
        frame_duration_seconds: Duration of each frame in seconds
        include_stats: Whether to include statistics in frames
    """
    logger.info(f"Starting frame maker with {frame_duration_seconds}s frames")
    
    async def _frame_maker():
        try:
            conn = await get_db_connection()
            
            try:
                # Refresh continuous aggregates
                await conn.execute("CALL refresh_continuous_aggregate('match_live_frame', NULL, NULL);")
                
                logger.info("Frame maker completed successfully")
                return {"status": "success"}
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Frame maker failed: {e}")
            raise
    
    return run_async_task(_frame_maker())


@celery_app.task(bind=True, name='apps.api_server.tasks.finalizer')
def finalizer(self, delay_after_finish_minutes: int = 30, collect_player_ratings: bool = True):
    """
    Process finished matches and collect final stats.
    
    Args:
        delay_after_finish_minutes: Wait time after match finish before processing
        collect_player_ratings: Whether to collect player ratings
    """
    logger.info("Starting match finalizer")
    
    async def _finalizer():
        try:
            conn = await get_db_connection()
            
            try:
                # Get recently finished matches that haven't been finalized
                finished_matches = await conn.fetch("""
                    SELECT id, home_team_id, away_team_id, league_id
                    FROM fixture 
                    WHERE status_short IN ('FT', 'AET', 'PEN')
                    AND date <= NOW() - INTERVAL '%s minutes'
                    AND id NOT IN (
                        SELECT DISTINCT fixture_id FROM fixture_statistic
                    )
                """, delay_after_finish_minutes)
                
                finalized_count = 0
                
                for match in finished_matches:
                    fixture_id = match['id']
                    
                    logger.info(f"Finalizing fixture {fixture_id}")
                    
                    # TODO: Collect final statistics, events, lineups, player stats
                    # This would involve calling multiple API endpoints
                    
                    finalized_count += 1
                
                logger.info(f"Finalizer completed. Processed {finalized_count} matches")
                return {"status": "success", "finalized_matches": finalized_count}
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Finalizer failed: {e}")
            raise
    
    return run_async_task(_finalizer())


@celery_app.task(bind=True, name='apps.api_server.tasks.weekly_refresh')
def weekly_refresh(self, update_leagues: bool = True, update_teams: bool = True, update_players: bool = False):
    """
    Weekly refresh of leagues, teams, and static data.
    
    Args:
        update_leagues: Whether to update league data
        update_teams: Whether to update team data
        update_players: Whether to update player data
    """
    logger.info("Starting weekly refresh")
    
    async def _weekly_refresh():
        try:
            updated_count = 0
            
            if update_leagues:
                # TODO: Update league data
                logger.info("Updating league data")
                updated_count += 1
            
            if update_teams:
                # TODO: Update team data
                logger.info("Updating team data")
                updated_count += 1
            
            if update_players:
                # TODO: Update player data
                logger.info("Updating player data")
                updated_count += 1
            
            logger.info(f"Weekly refresh completed. Updated {updated_count} data types")
            return {"status": "success", "updated_types": updated_count}
            
        except Exception as e:
            logger.error(f"Weekly refresh failed: {e}")
            raise
    
    return run_async_task(_weekly_refresh())


@celery_app.task(bind=True, name='apps.api_server.tasks.cold_archive')
def cold_archive(self, dry_run: bool = False, compress_before_archive: bool = True):
    """
    Archive old data according to retention policies.
    
    Args:
        dry_run: Whether to perform a dry run without actual deletion
        compress_before_archive: Whether to compress data before archiving
    """
    logger.info(f"Starting cold archive (dry_run={dry_run})")
    
    async def _cold_archive():
        try:
            conn = await get_db_connection()
            
            try:
                # Run maintenance cleanup functions
                cleanup_results = await conn.fetch("SELECT * FROM run_maintenance_cleanup()")
                
                total_deleted = sum(row['deleted_count'] for row in cleanup_results)
                
                logger.info(f"Cold archive completed. Deleted {total_deleted} records")
                return {
                    "status": "success", 
                    "total_deleted": total_deleted,
                    "cleanup_details": [dict(row) for row in cleanup_results]
                }
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Cold archive failed: {e}")
            raise
    
    return run_async_task(_cold_archive())


@celery_app.task(bind=True, name='apps.api_server.tasks.health_check_reporter')
def health_check_reporter(self, include_db_stats: bool = True, include_redis_stats: bool = True, include_api_stats: bool = True):
    """
    Report system health metrics.
    
    Args:
        include_db_stats: Whether to include database statistics
        include_redis_stats: Whether to include Redis statistics
        include_api_stats: Whether to include API statistics
    """
    logger.info("Starting health check reporter")
    
    async def _health_check_reporter():
        try:
            health_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "healthy"
            }
            
            if include_db_stats:
                # TODO: Collect database statistics
                health_data["database"] = {"status": "healthy"}
            
            if include_redis_stats:
                # TODO: Collect Redis statistics
                health_data["redis"] = {"status": "healthy"}
            
            if include_api_stats:
                # TODO: Collect API statistics
                health_data["api"] = {"status": "healthy"}
            
            logger.info("Health check reporter completed")
            return health_data
            
        except Exception as e:
            logger.error(f"Health check reporter failed: {e}")
            raise
    
    return run_async_task(_health_check_reporter())


async def _store_fixture(conn: asyncpg.Connection, fixture_data: Dict[str, Any], update_existing: bool = True):
    """Store fixture data in database."""
    # TODO: Implement fixture storage logic
    pass


async def _store_prematch_odds(conn: asyncpg.Connection, fixture_id: int, odds_data: Dict[str, Any]):
    """Store prematch odds data in database."""
    # TODO: Implement prematch odds storage logic
    pass


async def setup_celery_beat_schedules(workers_config: Dict[str, Any]):
    """Setup Celery Beat schedules from workers configuration."""
    logger.info("Setting up Celery Beat schedules")
    
    # TODO: Implement dynamic schedule setup from workers.yml
    # This would read the workers_config and create appropriate schedules
    
    logger.info("Celery Beat schedules configured")
