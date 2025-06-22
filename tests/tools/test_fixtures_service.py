"""
Test suite for FixturesService
Unit tests for the fixtures API wrapper.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from tools.fixtures_service import FixturesService


class TestFixturesService:
    """Test cases for FixturesService."""
    
    @pytest.fixture
    def service(self):
        """Create a FixturesService instance for testing."""
        return FixturesService()
    
    @pytest.fixture
    def mock_response_data(self):
        """Mock API response data."""
        return {
            "get": "fixtures",
            "parameters": {
                "league": "39",
                "season": "2024"
            },
            "errors": [],
            "results": 2,
            "paging": {
                "current": 1,
                "total": 1
            },
            "response": [
                {
                    "fixture": {
                        "id": 1035048,
                        "referee": "Anthony Taylor",
                        "timezone": "UTC",
                        "date": "2024-01-01T15:00:00+00:00",
                        "timestamp": 1704117600,
                        "periods": {
                            "first": 1704117600,
                            "second": 1704121200
                        },
                        "venue": {
                            "id": 556,
                            "name": "Old Trafford",
                            "city": "Manchester"
                        },
                        "status": {
                            "long": "Match Finished",
                            "short": "FT",
                            "elapsed": 90
                        }
                    },
                    "league": {
                        "id": 39,
                        "name": "Premier League",
                        "country": "England",
                        "logo": "https://media.api-sports.io/football/leagues/39.png",
                        "flag": "https://media.api-sports.io/flags/gb.svg",
                        "season": 2024,
                        "round": "Regular Season - 20"
                    },
                    "teams": {
                        "home": {
                            "id": 33,
                            "name": "Manchester United",
                            "logo": "https://media.api-sports.io/football/teams/33.png",
                            "winner": True
                        },
                        "away": {
                            "id": 34,
                            "name": "Newcastle",
                            "logo": "https://media.api-sports.io/football/teams/34.png",
                            "winner": False
                        }
                    },
                    "goals": {
                        "home": 2,
                        "away": 1
                    },
                    "score": {
                        "halftime": {
                            "home": 1,
                            "away": 0
                        },
                        "fulltime": {
                            "home": 2,
                            "away": 1
                        },
                        "extratime": {
                            "home": None,
                            "away": None
                        },
                        "penalty": {
                            "home": None,
                            "away": None
                        }
                    }
                }
            ]
        }
    
    def test_service_initialization(self, service):
        """Test service initialization."""
        assert service.endpoint == "fixtures"
        assert service.base_url == "https://api-football-v1.p.rapidapi.com/v3"
        assert "X-RapidAPI-Key" in service.headers
        assert "X-RapidAPI-Host" in service.headers
    
    @pytest.mark.asyncio
    async def test_fetch_with_league_and_season(self, service, mock_response_data):
        """Test fetching fixtures with league and season parameters."""
        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response_data
            
            result = await service.fetch(league=39, season=2024)
            
            mock_request.assert_called_once_with({
                'league': 39,
                'season': 2024
            })
            assert result == mock_response_data
            assert result['results'] == 2
            assert len(result['response']) == 1
    
    @pytest.mark.asyncio
    async def test_fetch_with_date_range(self, service, mock_response_data):
        """Test fetching fixtures with date range."""
        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response_data
            
            result = await service.fetch(
                from_="2024-01-01",
                to="2024-01-31"
            )
            
            mock_request.assert_called_once_with({
                'from': "2024-01-01",
                'to': "2024-01-31"
            })
            assert result == mock_response_data
    
    @pytest.mark.asyncio
    async def test_fetch_with_team_id(self, service, mock_response_data):
        """Test fetching fixtures for a specific team."""
        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response_data
            
            result = await service.fetch(team=33, season=2024)
            
            mock_request.assert_called_once_with({
                'team': 33,
                'season': 2024
            })
            assert result == mock_response_data
    
    @pytest.mark.asyncio
    async def test_fetch_with_fixture_id(self, service, mock_response_data):
        """Test fetching a specific fixture by ID."""
        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response_data
            
            result = await service.fetch(id=1035048)
            
            mock_request.assert_called_once_with({
                'id': 1035048
            })
            assert result == mock_response_data
    
    @pytest.mark.asyncio
    async def test_fetch_with_status_filter(self, service, mock_response_data):
        """Test fetching fixtures with status filter."""
        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response_data
            
            result = await service.fetch(league=39, season=2024, status="FT")
            
            mock_request.assert_called_once_with({
                'league': 39,
                'season': 2024,
                'status': "FT"
            })
            assert result == mock_response_data
    
    @pytest.mark.asyncio
    async def test_fetch_with_venue_filter(self, service, mock_response_data):
        """Test fetching fixtures with venue filter."""
        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response_data
            
            result = await service.fetch(league=39, season=2024, venue=556)
            
            mock_request.assert_called_once_with({
                'league': 39,
                'season': 2024,
                'venue': 556
            })
            assert result == mock_response_data
    
    @pytest.mark.asyncio
    async def test_fetch_with_round_filter(self, service, mock_response_data):
        """Test fetching fixtures with round filter."""
        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response_data
            
            result = await service.fetch(
                league=39, 
                season=2024, 
                round="Regular Season - 20"
            )
            
            mock_request.assert_called_once_with({
                'league': 39,
                'season': 2024,
                'round': "Regular Season - 20"
            })
            assert result == mock_response_data
    
    @pytest.mark.asyncio
    async def test_fetch_with_timezone(self, service, mock_response_data):
        """Test fetching fixtures with timezone parameter."""
        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response_data
            
            result = await service.fetch(
                league=39, 
                season=2024, 
                timezone="Europe/London"
            )
            
            mock_request.assert_called_once_with({
                'league': 39,
                'season': 2024,
                'timezone': "Europe/London"
            })
            assert result == mock_response_data
    
    @pytest.mark.asyncio
    async def test_fetch_no_parameters_raises_error(self, service):
        """Test that fetch raises error when no parameters provided."""
        with pytest.raises(ValueError, match="At least one parameter must be provided"):
            await service.fetch()
    
    @pytest.mark.asyncio
    async def test_fetch_api_error_handling(self, service):
        """Test API error handling."""
        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                await service.fetch(league=39, season=2024)
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, service, mock_response_data):
        """Test successful health check."""
        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response_data
            
            result = await service.health_check()
            
            assert result is True
            mock_request.assert_called_once_with({'league': 39, 'season': 2024})
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, service):
        """Test health check failure."""
        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = Exception("Connection failed")
            
            result = await service.health_check()
            
            assert result is False
    
    def test_validate_parameters_valid(self, service):
        """Test parameter validation with valid parameters."""
        params = {'league': 39, 'season': 2024}
        # Should not raise any exception
        service._validate_parameters(params)
    
    def test_validate_parameters_invalid_league(self, service):
        """Test parameter validation with invalid league."""
        params = {'league': 'invalid', 'season': 2024}
        with pytest.raises(ValueError, match="League must be an integer"):
            service._validate_parameters(params)
    
    def test_validate_parameters_invalid_season(self, service):
        """Test parameter validation with invalid season."""
        params = {'league': 39, 'season': 'invalid'}
        with pytest.raises(ValueError, match="Season must be an integer"):
            service._validate_parameters(params)
    
    def test_validate_parameters_invalid_team(self, service):
        """Test parameter validation with invalid team."""
        params = {'team': 'invalid', 'season': 2024}
        with pytest.raises(ValueError, match="Team must be an integer"):
            service._validate_parameters(params)
    
    def test_validate_parameters_invalid_date_format(self, service):
        """Test parameter validation with invalid date format."""
        params = {'from': 'invalid-date'}
        with pytest.raises(ValueError, match="Date must be in YYYY-MM-DD format"):
            service._validate_parameters(params)
