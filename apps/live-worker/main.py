"""
Footy-Brain v5 Live Worker
Real-time data ingestion worker for live matches (5-10s cycle).

This worker:
1. Monitors live matches from the database
2. Collects real-time odds, events, and statistics
3. Stores data in TimescaleDB hypertables
4. Publishes updates to Redis for WebSocket broadcasting
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
import yaml

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.live_odds_service import LiveOddsService
from tools.live_events_service import LiveEventsService
from tools.live_stats_service import LiveStatsService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LiveWorker:
    """Real-time data ingestion worker."""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL',
            'postgresql://footy:footy_secure_2024@localhost:5433/footy')
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6380/0')
        
        # API services
        self.odds_service = LiveOddsService()
        self.events_service = LiveEventsService()
        self.stats_service = LiveStatsService()
        
        # Connections
        self.db_conn: Optional[asyncpg.Connection] = None
        self.redis_client: Optional[redis.Redis] = None
        
        # Configuration
        self.cycle_interval = int(os.getenv('LIVE_WORKER_INTERVAL', '10'))  # seconds
        self.max_concurrent_matches = int(os.getenv('LIVE_WORKER_CONCURRENCY', '5'))
        
        # State
        self.running = False
        self.active_matches: Dict[int, Dict] = {}
        
    async def initialize(self):
        """Initialize database and Redis connections."""
        logger.info("Initializing Live Worker...")
        
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
            
            logger.info("Live Worker initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Live Worker: {e}")
            raise
    
    async def cleanup(self):
        """Clean up connections."""
        logger.info("Cleaning up Live Worker...")
        
        if self.db_conn:
            await self.db_conn.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Live Worker cleanup completed")
    
    async def get_live_matches(self) -> List[Dict[str, Any]]:
        """Get currently live matches from database."""
        query = """
            SELECT 
                id,
                home_team_id,
                away_team_id,
                league_id,
                status_short,
                status_elapsed,
                date
            FROM fixture 
            WHERE status_short IN ('1H', '2H', 'HT', 'ET', 'BT', 'P')
            AND date >= NOW() - INTERVAL '4 hours'
            AND date <= NOW() + INTERVAL '2 hours'
            ORDER BY date ASC
        """
        
        rows = await self.db_conn.fetch(query)
        
        matches = []
        for row in rows:
            matches.append({
                'fixture_id': row['id'],
                'home_team_id': row['home_team_id'],
                'away_team_id': row['away_team_id'],
                'league_id': row['league_id'],
                'status_short': row['status_short'],
                'status_elapsed': row['status_elapsed'],
                'date': row['date']
            })
        
        return matches
    
    async def collect_live_odds(self, fixture_id: int) -> List[Dict[str, Any]]:
        """Collect live odds for a fixture."""
        try:
            odds_data = await self.odds_service.fetch(fixture=fixture_id)
            
            if not odds_data or 'response' not in odds_data:
                return []
            
            odds_records = []
            timestamp = datetime.utcnow()
            
            for odds_entry in odds_data['response']:
                bookmaker_id = odds_entry.get('bookmaker', {}).get('id')
                
                for bet in odds_entry.get('bets', []):
                    bet_market_id = bet.get('id')
                    
                    for value in bet.get('values', []):
                        odds_records.append({
                            'fixture_id': fixture_id,
                            'bookmaker_id': bookmaker_id,
                            'bet_market_id': bet_market_id,
                            'bet_value': value.get('value'),
                            'odd_value': float(value.get('odd', 0)),
                            'timestamp': timestamp
                        })
            
            return odds_records
            
        except Exception as e:
            logger.error(f"Error collecting live odds for fixture {fixture_id}: {e}")
            return []
    
    async def collect_live_events(self, fixture_id: int) -> List[Dict[str, Any]]:
        """Collect live events for a fixture."""
        try:
            events_data = await self.events_service.fetch(fixture=fixture_id)
            
            if not events_data or 'response' not in events_data:
                return []
            
            events_records = []
            timestamp = datetime.utcnow()
            
            for event in events_data['response']:
                events_records.append({
                    'fixture_id': fixture_id,
                    'event_type': event.get('type'),
                    'event_detail': event.get('detail'),
                    'event_comments': event.get('comments'),
                    'timestamp': timestamp,
                    'match_minute': event.get('time', {}).get('elapsed'),
                    'match_minute_extra': event.get('time', {}).get('extra'),
                    'team_id': event.get('team', {}).get('id'),
                    'player_id': event.get('player', {}).get('id'),
                    'assist_player_id': event.get('assist', {}).get('id')
                })
            
            return events_records
            
        except Exception as e:
            logger.error(f"Error collecting live events for fixture {fixture_id}: {e}")
            return []
    
    async def collect_live_stats(self, fixture_id: int) -> List[Dict[str, Any]]:
        """Collect live statistics for a fixture."""
        try:
            stats_data = await self.stats_service.fetch(fixture=fixture_id)
            
            if not stats_data or 'response' not in stats_data:
                return []
            
            stats_records = []
            timestamp = datetime.utcnow()
            
            for team_stats in stats_data['response']:
                team_id = team_stats.get('team', {}).get('id')
                statistics = team_stats.get('statistics', [])
                
                # Convert statistics list to dict
                stats_dict = {}
                for stat in statistics:
                    stat_type = stat.get('type', '').lower().replace(' ', '_')
                    stat_value = stat.get('value')
                    
                    # Convert percentage strings to integers
                    if isinstance(stat_value, str) and stat_value.endswith('%'):
                        stat_value = int(stat_value.rstrip('%'))
                    elif stat_value is None:
                        stat_value = 0
                    
                    stats_dict[stat_type] = stat_value
                
                stats_records.append({
                    'fixture_id': fixture_id,
                    'team_id': team_id,
                    'timestamp': timestamp,
                    'shots_on_goal': stats_dict.get('shots_on_goal', 0),
                    'shots_off_goal': stats_dict.get('shots_off_goal', 0),
                    'total_shots': stats_dict.get('total_shots', 0),
                    'blocked_shots': stats_dict.get('blocked_shots', 0),
                    'shots_inside_box': stats_dict.get('shots_inside_box', 0),
                    'shots_outside_box': stats_dict.get('shots_outside_box', 0),
                    'fouls': stats_dict.get('fouls', 0),
                    'corner_kicks': stats_dict.get('corner_kicks', 0),
                    'offsides': stats_dict.get('offsides', 0),
                    'ball_possession': stats_dict.get('ball_possession', 0),
                    'yellow_cards': stats_dict.get('yellow_cards', 0),
                    'red_cards': stats_dict.get('red_cards', 0),
                    'goalkeeper_saves': stats_dict.get('goalkeeper_saves', 0),
                    'total_passes': stats_dict.get('total_passes', 0),
                    'passes_accurate': stats_dict.get('passes_accurate', 0),
                    'passes_percentage': stats_dict.get('passes_percentage', 0)
                })
            
            return stats_records
            
        except Exception as e:
            logger.error(f"Error collecting live stats for fixture {fixture_id}: {e}")
            return []
    
    async def store_live_data(self, odds: List[Dict], events: List[Dict], stats: List[Dict]):
        """Store live data in TimescaleDB hypertables."""
        try:
            # Store odds
            if odds:
                await self.db_conn.executemany("""
                    INSERT INTO live_odds_tick (
                        fixture_id, bookmaker_id, bet_market_id, bet_value, 
                        odd_value, timestamp
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                """, [
                    (
                        record['fixture_id'],
                        record['bookmaker_id'],
                        record['bet_market_id'],
                        record['bet_value'],
                        record['odd_value'],
                        record['timestamp']
                    ) for record in odds
                ])
            
            # Store events
            if events:
                await self.db_conn.executemany("""
                    INSERT INTO live_event_tick (
                        fixture_id, event_type, event_detail, event_comments,
                        timestamp, match_minute, match_minute_extra,
                        team_id, player_id, assist_player_id
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, [
                    (
                        record['fixture_id'],
                        record['event_type'],
                        record['event_detail'],
                        record['event_comments'],
                        record['timestamp'],
                        record['match_minute'],
                        record['match_minute_extra'],
                        record['team_id'],
                        record['player_id'],
                        record['assist_player_id']
                    ) for record in events
                ])
            
            # Store stats
            if stats:
                await self.db_conn.executemany("""
                    INSERT INTO live_stats_tick (
                        fixture_id, team_id, timestamp,
                        shots_on_goal, shots_off_goal, total_shots, blocked_shots,
                        shots_inside_box, shots_outside_box, fouls, corner_kicks,
                        offsides, ball_possession, yellow_cards, red_cards,
                        goalkeeper_saves, total_passes, passes_accurate, passes_percentage
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19)
                """, [
                    (
                        record['fixture_id'],
                        record['team_id'],
                        record['timestamp'],
                        record['shots_on_goal'],
                        record['shots_off_goal'],
                        record['total_shots'],
                        record['blocked_shots'],
                        record['shots_inside_box'],
                        record['shots_outside_box'],
                        record['fouls'],
                        record['corner_kicks'],
                        record['offsides'],
                        record['ball_possession'],
                        record['yellow_cards'],
                        record['red_cards'],
                        record['goalkeeper_saves'],
                        record['total_passes'],
                        record['passes_accurate'],
                        record['passes_percentage']
                    ) for record in stats
                ])
            
            logger.debug(f"Stored {len(odds)} odds, {len(events)} events, {len(stats)} stats")
            
        except Exception as e:
            logger.error(f"Error storing live data: {e}")
            raise
    
    async def publish_to_redis(self, fixture_id: int, odds: List[Dict], events: List[Dict], stats: List[Dict]):
        """Publish live data to Redis for WebSocket broadcasting."""
        try:
            timestamp = datetime.utcnow().isoformat()
            
            # Publish odds updates
            if odds:
                await self.redis_client.publish('live-odds', {
                    'fixture_id': fixture_id,
                    'timestamp': timestamp,
                    'odds': odds[-10:]  # Last 10 odds updates
                })
            
            # Publish event updates
            if events:
                await self.redis_client.publish('live-events', {
                    'fixture_id': fixture_id,
                    'timestamp': timestamp,
                    'events': events
                })
            
            # Publish stats updates
            if stats:
                await self.redis_client.publish('live-stats', {
                    'fixture_id': fixture_id,
                    'timestamp': timestamp,
                    'stats': stats
                })
            
        except Exception as e:
            logger.error(f"Error publishing to Redis: {e}")
    
    async def process_live_match(self, match: Dict[str, Any]):
        """Process a single live match."""
        fixture_id = match['fixture_id']
        
        try:
            logger.debug(f"Processing live match {fixture_id}")
            
            # Collect data concurrently
            odds_task = asyncio.create_task(self.collect_live_odds(fixture_id))
            events_task = asyncio.create_task(self.collect_live_events(fixture_id))
            stats_task = asyncio.create_task(self.collect_live_stats(fixture_id))
            
            odds, events, stats = await asyncio.gather(
                odds_task, events_task, stats_task,
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(odds, Exception):
                logger.error(f"Odds collection failed for {fixture_id}: {odds}")
                odds = []
            
            if isinstance(events, Exception):
                logger.error(f"Events collection failed for {fixture_id}: {events}")
                events = []
            
            if isinstance(stats, Exception):
                logger.error(f"Stats collection failed for {fixture_id}: {stats}")
                stats = []
            
            # Store and publish data
            if odds or events or stats:
                await self.store_live_data(odds, events, stats)
                await self.publish_to_redis(fixture_id, odds, events, stats)
            
            logger.info(f"Processed fixture {fixture_id}: {len(odds)} odds, {len(events)} events, {len(stats)} stats")
            
        except Exception as e:
            logger.error(f"Error processing live match {fixture_id}: {e}")
    
    async def run_cycle(self):
        """Run one data collection cycle."""
        try:
            # Get live matches
            live_matches = await self.get_live_matches()
            
            if not live_matches:
                logger.debug("No live matches found")
                return
            
            logger.info(f"Processing {len(live_matches)} live matches")
            
            # Process matches with concurrency limit
            semaphore = asyncio.Semaphore(self.max_concurrent_matches)
            
            async def process_with_semaphore(match):
                async with semaphore:
                    await self.process_live_match(match)
            
            # Process all matches concurrently
            tasks = [process_with_semaphore(match) for match in live_matches]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.info(f"Completed cycle for {len(live_matches)} matches")
            
        except Exception as e:
            logger.error(f"Error in run cycle: {e}")
    
    async def run(self):
        """Main worker loop."""
        logger.info(f"Starting Live Worker with {self.cycle_interval}s interval")
        self.running = True
        
        try:
            while self.running:
                cycle_start = datetime.utcnow()
                
                await self.run_cycle()
                
                # Calculate sleep time to maintain interval
                cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
                sleep_time = max(0, self.cycle_interval - cycle_duration)
                
                if sleep_time > 0:
                    logger.debug(f"Cycle completed in {cycle_duration:.2f}s, sleeping for {sleep_time:.2f}s")
                    await asyncio.sleep(sleep_time)
                else:
                    logger.warning(f"Cycle took {cycle_duration:.2f}s, longer than interval {self.cycle_interval}s")
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Fatal error in worker loop: {e}")
            raise
        finally:
            self.running = False
            logger.info("Live Worker stopped")


async def main():
    """Main entry point."""
    worker = LiveWorker()
    
    try:
        await worker.initialize()
        await worker.run()
    finally:
        await worker.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
