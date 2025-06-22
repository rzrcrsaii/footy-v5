"""
Test suite for Live Worker
Unit tests for the real-time data ingestion worker.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from apps.live_worker.main import LiveWorker


class TestLiveWorker:
    """Test cases for LiveWorker."""
    
    @pytest.fixture
    def worker(self):
        """Create a LiveWorker instance for testing."""
        with patch.dict('os.environ', {
            'DATABASE_URL': 'postgresql://test:test@localhost:5432/test',
            'REDIS_URL': 'redis://localhost:6379/0'
        }):
            return LiveWorker()
    
    @pytest.fixture
    def mock_live_matches(self):
        """Mock live matches data."""
        return [
            {
                'fixture_id': 1035048,
                'home_team_id': 33,
                'away_team_id': 34,
                'league_id': 39,
                'status_short': '1H',
                'status_elapsed': 45,
                'date': '2024-01-01T15:00:00+00:00'
            },
            {
                'fixture_id': 1035049,
                'home_team_id': 35,
                'away_team_id': 36,
                'league_id': 39,
                'status_short': '2H',
                'status_elapsed': 67,
                'date': '2024-01-01T17:00:00+00:00'
            }
        ]
    
    def test_worker_initialization(self, worker):
        """Test worker initialization."""
        assert worker.cycle_interval == 10
        assert worker.max_concurrent_matches == 5
        assert worker.running is False
        assert worker.active_matches == {}
    
    @pytest.mark.asyncio
    async def test_initialize_connections(self, worker):
        """Test database and Redis connection initialization."""
        with patch('asyncpg.connect') as mock_db, \
             patch('redis.asyncio.from_url') as mock_redis:
            
            mock_db.return_value = AsyncMock()
            mock_redis_client = AsyncMock()
            mock_redis.return_value = mock_redis_client
            mock_redis_client.ping = AsyncMock()
            
            await worker.initialize()
            
            assert worker.db_conn is not None
            assert worker.redis_client is not None
            mock_db.assert_called_once()
            mock_redis.assert_called_once()
            mock_redis_client.ping.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_live_matches(self, worker, mock_live_matches):
        """Test getting live matches from database."""
        worker.db_conn = AsyncMock()
        worker.db_conn.fetch.return_value = [
            {
                'id': match['fixture_id'],
                'home_team_id': match['home_team_id'],
                'away_team_id': match['away_team_id'],
                'league_id': match['league_id'],
                'status_short': match['status_short'],
                'status_elapsed': match['status_elapsed'],
                'date': match['date']
            } for match in mock_live_matches
        ]
        
        matches = await worker.get_live_matches()
        
        assert len(matches) == 2
        assert matches[0]['fixture_id'] == 1035048
        assert matches[1]['fixture_id'] == 1035049
        worker.db_conn.fetch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_collect_live_odds(self, worker):
        """Test collecting live odds for a fixture."""
        worker.odds_service = AsyncMock()
        worker.odds_service.fetch.return_value = {
            'response': [
                {
                    'bookmaker': {'id': 1},
                    'bets': [
                        {
                            'id': 1,
                            'values': [
                                {'value': '1', 'odd': '2.10'},
                                {'value': 'X', 'odd': '3.20'},
                                {'value': '2', 'odd': '3.50'}
                            ]
                        }
                    ]
                }
            ]
        }
        
        odds = await worker.collect_live_odds(1035048)
        
        assert len(odds) == 3
        assert odds[0]['bet_value'] == '1'
        assert odds[0]['odd_value'] == 2.10
        worker.odds_service.fetch.assert_called_once_with(fixture=1035048)
    
    @pytest.mark.asyncio
    async def test_collect_live_events(self, worker):
        """Test collecting live events for a fixture."""
        worker.events_service = AsyncMock()
        worker.events_service.fetch.return_value = {
            'response': [
                {
                    'type': 'Goal',
                    'detail': 'Normal Goal',
                    'comments': None,
                    'time': {'elapsed': 23, 'extra': None},
                    'team': {'id': 33},
                    'player': {'id': 123},
                    'assist': {'id': 456}
                }
            ]
        }
        
        events = await worker.collect_live_events(1035048)
        
        assert len(events) == 1
        assert events[0]['event_type'] == 'Goal'
        assert events[0]['match_minute'] == 23
        worker.events_service.fetch.assert_called_once_with(fixture=1035048)
    
    @pytest.mark.asyncio
    async def test_collect_live_stats(self, worker):
        """Test collecting live statistics for a fixture."""
        worker.stats_service = AsyncMock()
        worker.stats_service.fetch.return_value = {
            'response': [
                {
                    'team': {'id': 33},
                    'statistics': [
                        {'type': 'Shots on Goal', 'value': 5},
                        {'type': 'Ball Possession', 'value': '65%'},
                        {'type': 'Total Shots', 'value': 8}
                    ]
                }
            ]
        }
        
        stats = await worker.collect_live_stats(1035048)
        
        assert len(stats) == 1
        assert stats[0]['team_id'] == 33
        assert stats[0]['shots_on_goal'] == 5
        assert stats[0]['ball_possession'] == 65
        worker.stats_service.fetch.assert_called_once_with(fixture=1035048)
    
    @pytest.mark.asyncio
    async def test_store_live_data(self, worker):
        """Test storing live data in database."""
        worker.db_conn = AsyncMock()
        
        odds = [{'fixture_id': 1, 'bookmaker_id': 1, 'bet_market_id': 1, 
                'bet_value': '1', 'odd_value': 2.10, 'timestamp': '2024-01-01T15:00:00'}]
        events = [{'fixture_id': 1, 'event_type': 'Goal', 'timestamp': '2024-01-01T15:00:00'}]
        stats = [{'fixture_id': 1, 'team_id': 33, 'shots_on_goal': 5, 'timestamp': '2024-01-01T15:00:00'}]
        
        await worker.store_live_data(odds, events, stats)
        
        # Should call executemany for each data type
        assert worker.db_conn.executemany.call_count == 3
    
    @pytest.mark.asyncio
    async def test_publish_to_redis(self, worker):
        """Test publishing live data to Redis."""
        worker.redis_client = AsyncMock()
        
        odds = [{'fixture_id': 1, 'odd_value': 2.10}]
        events = [{'fixture_id': 1, 'event_type': 'Goal'}]
        stats = [{'fixture_id': 1, 'shots_on_goal': 5}]
        
        await worker.publish_to_redis(1, odds, events, stats)
        
        # Should publish to Redis channels
        assert worker.redis_client.publish.call_count == 3
    
    @pytest.mark.asyncio
    async def test_process_live_match(self, worker):
        """Test processing a single live match."""
        match = {
            'fixture_id': 1035048,
            'home_team_id': 33,
            'away_team_id': 34,
            'status_short': '1H'
        }
        
        with patch.object(worker, 'collect_live_odds') as mock_odds, \
             patch.object(worker, 'collect_live_events') as mock_events, \
             patch.object(worker, 'collect_live_stats') as mock_stats, \
             patch.object(worker, 'store_live_data') as mock_store, \
             patch.object(worker, 'publish_to_redis') as mock_publish:
            
            mock_odds.return_value = [{'odd_value': 2.10}]
            mock_events.return_value = [{'event_type': 'Goal'}]
            mock_stats.return_value = [{'shots_on_goal': 5}]
            
            await worker.process_live_match(match)
            
            mock_odds.assert_called_once_with(1035048)
            mock_events.assert_called_once_with(1035048)
            mock_stats.assert_called_once_with(1035048)
            mock_store.assert_called_once()
            mock_publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_cycle(self, worker, mock_live_matches):
        """Test running one data collection cycle."""
        with patch.object(worker, 'get_live_matches') as mock_get_matches, \
             patch.object(worker, 'process_live_match') as mock_process:
            
            mock_get_matches.return_value = mock_live_matches
            mock_process.return_value = None
            
            await worker.run_cycle()
            
            mock_get_matches.assert_called_once()
            assert mock_process.call_count == 2  # Two matches
    
    @pytest.mark.asyncio
    async def test_error_handling_in_collect_odds(self, worker):
        """Test error handling in odds collection."""
        worker.odds_service = AsyncMock()
        worker.odds_service.fetch.side_effect = Exception("API Error")
        
        odds = await worker.collect_live_odds(1035048)
        
        assert odds == []  # Should return empty list on error
    
    @pytest.mark.asyncio
    async def test_cleanup(self, worker):
        """Test worker cleanup."""
        worker.db_conn = AsyncMock()
        worker.redis_client = AsyncMock()
        
        await worker.cleanup()
        
        worker.db_conn.close.assert_called_once()
        worker.redis_client.close.assert_called_once()
