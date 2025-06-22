"""
Test suite for Fixtures Router
Integration tests for the fixtures API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from apps.api_server.main import app


class TestFixturesRouter:
    """Test cases for fixtures API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_fixture_data(self):
        """Mock fixture data for testing."""
        return {
            "id": 1035048,
            "referee": "Anthony Taylor",
            "timezone": "UTC",
            "date": "2024-01-01T15:00:00+00:00",
            "timestamp": 1704117600,
            "status_short": "FT",
            "status_long": "Match Finished",
            "status_elapsed": 90,
            "status_extra": None,
            "league_id": 39,
            "league_name": "Premier League",
            "season_year": 2024,
            "round": "Regular Season - 20",
            "home_team_id": 33,
            "home_team_name": "Manchester United",
            "home_team_logo": "https://media.api-sports.io/football/teams/33.png",
            "away_team_id": 34,
            "away_team_name": "Newcastle",
            "away_team_logo": "https://media.api-sports.io/football/teams/34.png",
            "home_goals": 2,
            "away_goals": 1,
            "home_goals_ht": 1,
            "away_goals_ht": 0,
            "home_goals_et": 0,
            "away_goals_et": 0,
            "home_goals_pen": 0,
            "away_goals_pen": 0,
            "venue_id": 556,
            "venue_name": "Old Trafford",
            "venue_city": "Manchester",
            "created_at": "2024-01-01T10:00:00+00:00",
            "updated_at": "2024-01-01T17:00:00+00:00"
        }
    
    def test_get_fixtures_success(self, client, mock_fixture_data):
        """Test successful fixtures retrieval."""
        with patch('apps.api_server.deps.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            # Mock database query result
            mock_result = AsyncMock()
            mock_result.fetchall.return_value = [(mock_fixture_data,)]
            mock_session.execute.return_value = mock_result
            
            response = client.get("/api/v1/fixtures")
            
            assert response.status_code == 200
            data = response.json()
            assert "fixtures" in data
            assert "total" in data
            assert "page" in data
            assert "per_page" in data
    
    def test_get_fixtures_with_filters(self, client):
        """Test fixtures retrieval with filters."""
        with patch('apps.api_server.deps.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_result = AsyncMock()
            mock_result.fetchall.return_value = []
            mock_session.execute.return_value = mock_result
            
            response = client.get("/api/v1/fixtures", params={
                "league_id": 39,
                "season_year": 2024,
                "status": "FT",
                "page": 1,
                "per_page": 20
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["page"] == 1
            assert data["per_page"] == 20
    
    def test_get_fixtures_pagination(self, client):
        """Test fixtures pagination."""
        with patch('apps.api_server.deps.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_result = AsyncMock()
            mock_result.fetchall.return_value = []
            mock_session.execute.return_value = mock_result
            
            response = client.get("/api/v1/fixtures", params={
                "page": 2,
                "per_page": 10
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["page"] == 2
            assert data["per_page"] == 10
    
    def test_get_fixtures_invalid_pagination(self, client):
        """Test fixtures with invalid pagination parameters."""
        response = client.get("/api/v1/fixtures", params={
            "page": 0,  # Invalid: must be >= 1
            "per_page": 10
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_get_fixture_by_id_success(self, client, mock_fixture_data):
        """Test successful single fixture retrieval."""
        with patch('apps.api_server.deps.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_result = AsyncMock()
            mock_result.first.return_value = (mock_fixture_data,)
            mock_session.execute.return_value = mock_result
            
            response = client.get("/api/v1/fixtures/1035048")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1035048
            assert data["home_team_name"] == "Manchester United"
            assert data["away_team_name"] == "Newcastle"
    
    def test_get_fixture_by_id_not_found(self, client):
        """Test fixture not found."""
        with patch('apps.api_server.deps.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_result = AsyncMock()
            mock_result.first.return_value = None
            mock_session.execute.return_value = mock_result
            
            response = client.get("/api/v1/fixtures/999999")
            
            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Fixture not found"
    
    def test_get_today_live_fixtures_success(self, client, mock_fixture_data):
        """Test today's live fixtures retrieval."""
        with patch('apps.api_server.deps.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            # Mock live fixture data
            live_fixture = mock_fixture_data.copy()
            live_fixture["status_short"] = "1H"
            live_fixture["status_elapsed"] = 45
            
            mock_result = AsyncMock()
            mock_result.fetchall.return_value = [(live_fixture,)]
            mock_session.execute.return_value = mock_result
            
            response = client.get("/api/v1/fixtures/today/live")
            
            assert response.status_code == 200
            data = response.json()
            assert "date" in data
            assert "fixtures" in data
            assert "total" in data
            assert data["total"] == 1
    
    def test_get_today_live_fixtures_empty(self, client):
        """Test today's live fixtures when no matches."""
        with patch('apps.api_server.deps.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_result = AsyncMock()
            mock_result.fetchall.return_value = []
            mock_session.execute.return_value = mock_result
            
            response = client.get("/api/v1/fixtures/today/live")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 0
            assert len(data["fixtures"]) == 0
    
    def test_get_fixtures_sorting(self, client):
        """Test fixtures sorting."""
        with patch('apps.api_server.deps.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_result = AsyncMock()
            mock_result.fetchall.return_value = []
            mock_session.execute.return_value = mock_result
            
            response = client.get("/api/v1/fixtures", params={
                "sort_by": "date",
                "sort_order": "asc"
            })
            
            assert response.status_code == 200
    
    def test_get_fixtures_invalid_sort_order(self, client):
        """Test fixtures with invalid sort order."""
        response = client.get("/api/v1/fixtures", params={
            "sort_by": "date",
            "sort_order": "invalid"  # Must be 'asc' or 'desc'
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_get_fixtures_database_error(self, client):
        """Test fixtures endpoint with database error."""
        with patch('apps.api_server.deps.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            mock_session.execute.side_effect = Exception("Database error")
            
            response = client.get("/api/v1/fixtures")
            
            assert response.status_code == 500
            data = response.json()
            assert data["detail"] == "Internal server error"
    
    def test_get_fixtures_with_team_filter(self, client):
        """Test fixtures filtering by team."""
        with patch('apps.api_server.deps.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_result = AsyncMock()
            mock_result.fetchall.return_value = []
            mock_session.execute.return_value = mock_result
            
            response = client.get("/api/v1/fixtures", params={
                "team_id": 33  # Manchester United
            })
            
            assert response.status_code == 200
    
    def test_get_fixtures_with_date_range(self, client):
        """Test fixtures filtering by date range."""
        with patch('apps.api_server.deps.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_result = AsyncMock()
            mock_result.fetchall.return_value = []
            mock_session.execute.return_value = mock_result
            
            response = client.get("/api/v1/fixtures", params={
                "date_from": "2024-01-01",
                "date_to": "2024-01-31"
            })
            
            assert response.status_code == 200
    
    def test_get_fixtures_rate_limiting(self, client):
        """Test rate limiting on fixtures endpoint."""
        # This would require actual rate limiting implementation
        # For now, just test that the endpoint accepts requests
        with patch('apps.api_server.deps.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_result = AsyncMock()
            mock_result.fetchall.return_value = []
            mock_session.execute.return_value = mock_result
            
            response = client.get("/api/v1/fixtures")
            assert response.status_code == 200
