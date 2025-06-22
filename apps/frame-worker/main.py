"""
Footy-Brain v5 Frame Worker
1-minute summary composer for live data aggregation.

This worker:
1. Aggregates live ticks into 1-minute frames
2. Refreshes TimescaleDB continuous aggregates
3. Publishes frame summaries to Redis
4. Maintains data quality and consistency
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import asyncpg
import redis.asyncio as redis

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FrameWorker:
    """1-minute frame aggregation worker."""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL',
            'postgresql://footy:footy_secure_2024@localhost:5433/footy')
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        
        # Connections
        self.db_conn: Optional[asyncpg.Connection] = None
        self.redis_client: Optional[redis.Redis] = None
        
        # Configuration
        self.cycle_interval = int(os.getenv('FRAME_WORKER_INTERVAL', '60'))  # seconds
        self.frame_duration = 60  # 1 minute frames
        
        # State
        self.running = False
        
    async def initialize(self):
        """Initialize database and Redis connections."""
        logger.info("Initializing Frame Worker...")
        
        try:
            # Connect to database
            self.db_conn = await asyncpg.connect(self.database_url)
            logger.info("Database connection established")
            
            # Connect to Redis
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis connection established")
            
            logger.info("Frame Worker initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Frame Worker: {e}")
            raise
    
    async def cleanup(self):
        """Clean up connections."""
        logger.info("Cleaning up Frame Worker...")
        
        if self.db_conn:
            await self.db_conn.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Frame Worker cleanup completed")
    
    async def refresh_continuous_aggregates(self):
        """Refresh TimescaleDB continuous aggregates."""
        try:
            logger.info("Refreshing continuous aggregates...")
            
            # List of continuous aggregates to refresh
            aggregates = [
                'live_odds_tick_ohlc_1m',
                'live_event_summary_1m',
                'live_stats_progression_5m',
                'match_live_frame',
                'bookmaker_odds_comparison_5m'
            ]
            
            for aggregate in aggregates:
                try:
                    # Refresh the last 2 hours of data
                    await self.db_conn.execute(f"""
                        CALL refresh_continuous_aggregate(
                            '{aggregate}', 
                            NOW() - INTERVAL '2 hours', 
                            NOW()
                        );
                    """)
                    logger.debug(f"Refreshed {aggregate}")
                    
                except Exception as e:
                    logger.error(f"Error refreshing {aggregate}: {e}")
            
            logger.info("Continuous aggregates refresh completed")
            
        except Exception as e:
            logger.error(f"Error refreshing continuous aggregates: {e}")
            raise
    
    async def get_active_fixtures(self) -> List[int]:
        """Get fixtures that have recent live data."""
        query = """
            SELECT DISTINCT fixture_id
            FROM (
                SELECT fixture_id FROM live_odds_tick 
                WHERE timestamp >= NOW() - INTERVAL '10 minutes'
                UNION
                SELECT fixture_id FROM live_event_tick 
                WHERE timestamp >= NOW() - INTERVAL '10 minutes'
                UNION
                SELECT fixture_id FROM live_stats_tick 
                WHERE timestamp >= NOW() - INTERVAL '10 minutes'
            ) active_fixtures
        """
        
        rows = await self.db_conn.fetch(query)
        return [row['fixture_id'] for row in rows]
    
    async def generate_frame_summary(self, fixture_id: int) -> Optional[Dict[str, Any]]:
        """Generate 1-minute frame summary for a fixture."""
        try:
            # Get the latest frame data
            query = """
                SELECT 
                    bucket,
                    fixture_id,
                    home_team_id,
                    away_team_id,
                    status_short,
                    status_elapsed,
                    home_goals,
                    away_goals,
                    avg_home_win_odd,
                    avg_draw_odd,
                    avg_away_win_odd,
                    home_odd_change,
                    away_odd_change,
                    total_events,
                    goals,
                    cards,
                    substitutions,
                    odds_ticks,
                    event_ticks
                FROM match_live_frame
                WHERE fixture_id = $1
                AND bucket >= NOW() - INTERVAL '2 minutes'
                ORDER BY bucket DESC
                LIMIT 1
            """
            
            row = await self.db_conn.fetchrow(query, fixture_id)
            
            if not row:
                return None
            
            # Get latest team stats
            stats_query = """
                SELECT 
                    team_id,
                    ball_possession,
                    total_shots,
                    shots_on_goal,
                    corner_kicks,
                    fouls
                FROM live_stats_progression_5m
                WHERE fixture_id = $1
                AND bucket >= NOW() - INTERVAL '5 minutes'
                ORDER BY bucket DESC
                LIMIT 2
            """
            
            stats_rows = await self.db_conn.fetch(stats_query, fixture_id)
            
            # Process stats
            home_stats = {}
            away_stats = {}
            
            for stat in stats_rows:
                if stat['team_id'] == row['home_team_id']:
                    home_stats = {
                        'possession': stat['ball_possession'],
                        'shots': stat['total_shots'],
                        'shots_on_goal': stat['shots_on_goal'],
                        'corners': stat['corner_kicks'],
                        'fouls': stat['fouls']
                    }
                elif stat['team_id'] == row['away_team_id']:
                    away_stats = {
                        'possession': stat['ball_possession'],
                        'shots': stat['total_shots'],
                        'shots_on_goal': stat['shots_on_goal'],
                        'corners': stat['corner_kicks'],
                        'fouls': stat['fouls']
                    }
            
            frame_summary = {
                'timestamp': row['bucket'].isoformat(),
                'fixture_id': fixture_id,
                'match_info': {
                    'home_team_id': row['home_team_id'],
                    'away_team_id': row['away_team_id'],
                    'status': row['status_short'],
                    'elapsed': row['status_elapsed'],
                    'score': {
                        'home': row['home_goals'],
                        'away': row['away_goals']
                    }
                },
                'odds': {
                    'home_win': float(row['avg_home_win_odd']) if row['avg_home_win_odd'] else None,
                    'draw': float(row['avg_draw_odd']) if row['avg_draw_odd'] else None,
                    'away_win': float(row['avg_away_win_odd']) if row['avg_away_win_odd'] else None,
                    'home_change': float(row['home_odd_change']) if row['home_odd_change'] else None,
                    'away_change': float(row['away_odd_change']) if row['away_odd_change'] else None
                },
                'events': {
                    'total': row['total_events'],
                    'goals': row['goals'],
                    'cards': row['cards'],
                    'substitutions': row['substitutions']
                },
                'activity': {
                    'odds_ticks': row['odds_ticks'],
                    'event_ticks': row['event_ticks']
                },
                'stats': {
                    'home': home_stats,
                    'away': away_stats
                }
            }
            
            return frame_summary
            
        except Exception as e:
            logger.error(f"Error generating frame summary for fixture {fixture_id}: {e}")
            return None
    
    async def publish_frame_summaries(self, summaries: List[Dict[str, Any]]):
        """Publish frame summaries to Redis."""
        try:
            if not summaries:
                return
            
            # Publish individual fixture frames
            for summary in summaries:
                await self.redis_client.publish('live-frame', summary)
            
            # Publish batch summary
            batch_summary = {
                'type': 'frame_batch',
                'timestamp': datetime.utcnow().isoformat(),
                'fixture_count': len(summaries),
                'fixtures': [s['fixture_id'] for s in summaries]
            }
            
            await self.redis_client.publish('live-feed', batch_summary)
            
            logger.debug(f"Published {len(summaries)} frame summaries to Redis")
            
        except Exception as e:
            logger.error(f"Error publishing frame summaries: {e}")
    
    async def cleanup_old_data(self):
        """Clean up old temporary data and maintain data quality."""
        try:
            # This runs less frequently (every 10 cycles)
            if datetime.utcnow().minute % 10 != 0:
                return
            
            logger.info("Running data cleanup...")
            
            # Clean up very old live ticks (older than retention policy)
            cleanup_queries = [
                "DELETE FROM live_odds_tick WHERE timestamp < NOW() - INTERVAL '30 days'",
                "DELETE FROM live_event_tick WHERE timestamp < NOW() - INTERVAL '90 days'", 
                "DELETE FROM live_stats_tick WHERE timestamp < NOW() - INTERVAL '60 days'"
            ]
            
            for query in cleanup_queries:
                try:
                    result = await self.db_conn.execute(query)
                    logger.debug(f"Cleanup query executed: {result}")
                except Exception as e:
                    logger.error(f"Error in cleanup query: {e}")
            
            # Update system statistics
            await self.db_conn.execute("""
                INSERT INTO system_config (key, value, description)
                VALUES ('last_frame_cleanup', $1, 'Last frame worker cleanup time')
                ON CONFLICT (key) DO UPDATE SET 
                    value = EXCLUDED.value,
                    updated_at = NOW()
            """, datetime.utcnow().isoformat())
            
            logger.info("Data cleanup completed")
            
        except Exception as e:
            logger.error(f"Error in data cleanup: {e}")
    
    async def run_cycle(self):
        """Run one frame generation cycle."""
        try:
            cycle_start = datetime.utcnow()
            
            # Refresh continuous aggregates
            await self.refresh_continuous_aggregates()
            
            # Get active fixtures
            active_fixtures = await self.get_active_fixtures()
            
            if not active_fixtures:
                logger.debug("No active fixtures found")
                return
            
            logger.info(f"Generating frames for {len(active_fixtures)} active fixtures")
            
            # Generate frame summaries
            summaries = []
            for fixture_id in active_fixtures:
                summary = await self.generate_frame_summary(fixture_id)
                if summary:
                    summaries.append(summary)
            
            # Publish summaries
            if summaries:
                await self.publish_frame_summaries(summaries)
            
            # Periodic cleanup
            await self.cleanup_old_data()
            
            cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
            logger.info(f"Frame cycle completed in {cycle_duration:.2f}s for {len(summaries)} fixtures")
            
        except Exception as e:
            logger.error(f"Error in frame cycle: {e}")
    
    async def run(self):
        """Main worker loop."""
        logger.info(f"Starting Frame Worker with {self.cycle_interval}s interval")
        self.running = True
        
        try:
            while self.running:
                cycle_start = datetime.utcnow()
                
                await self.run_cycle()
                
                # Calculate sleep time to maintain interval
                cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
                sleep_time = max(0, self.cycle_interval - cycle_duration)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                else:
                    logger.warning(f"Frame cycle took {cycle_duration:.2f}s, longer than interval {self.cycle_interval}s")
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Fatal error in frame worker loop: {e}")
            raise
        finally:
            self.running = False
            logger.info("Frame Worker stopped")


async def main():
    """Main entry point."""
    worker = FrameWorker()
    
    try:
        await worker.initialize()
        await worker.run()
    finally:
        await worker.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
