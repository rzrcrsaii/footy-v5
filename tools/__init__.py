"""
API Football Tools Package

Bu paket API Football servisleri için gerekli tüm araçları içerir.
"""

# Version
__version__ = "1.0.0"

# Import ana sınıflar
from .api_config import APIConfig, get_config
from .base_service import BaseService
from .error_handler import ErrorHandler, handle_api_response

# Import servisler
from .fixtures_service import FixturesService
from .countries_service import CountriesService
from .leagues_service import LeaguesService
from .leagues_txt_service import LeaguesTxtService
from .teams_service import TeamsService
from .teamsinfo_service import TeamsInfoService
from .standings_service import StandingsService
from .fixtures_round_service import FixturesRoundService
from .timezone_service import TimezoneService
from .seasons_service import SeasonsService

# Import odds services
from .odds_live_service import OddsLiveService
from .odds_live_bets_service import OddsLiveBetsService
from .prematch_odds_service import PrematchOddsService
from .prematch_bets_service import PrematchBetsService
from .prematch_bookmakers_service import PrematchBookmakersService

# Import fixture detail services
from .fixture_events_service import FixtureEventsService
from .fixture_statistics_service import FixtureStatisticsService
from .fixture_lineups_service import FixtureLineupsService
from .fixture_h2h_service import FixtureH2HService

# Import player services
from .player_profiles_service import PlayerProfilesService
from .player_statistics_service import PlayerStatisticsService
from .player_squads_service import PlayerSquadsService

__all__ = [
    'APIConfig',
    'get_config',
    'BaseService',
    'ErrorHandler',
    'handle_api_response',
    'FixturesService',
    'CountriesService',
    'LeaguesService',
    'LeaguesTxtService',
    'TeamsService',
    'TeamsInfoService',
    'StandingsService',
    'FixturesRoundService',
    'TimezoneService',
    'SeasonsService',
    'OddsLiveService',
    'OddsLiveBetsService',
    'PrematchOddsService',
    'PrematchBetsService',
    'PrematchBookmakersService',
    'FixtureEventsService',
    'FixtureStatisticsService',
    'FixtureLineupsService',
    'FixtureH2HService',
    'PlayerProfilesService',
    'PlayerStatisticsService',
    'PlayerSquadsService'
]
