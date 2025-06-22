"""
API Football Leagues Service Module

Bu modül API Football Leagues endpoint'i için servis sınıfını içerir.
Mevcut lig ve kupa listesini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional, Union
from .base_service import BaseService
from .api_config import APIConfig


class LeaguesService(BaseService):
    """
    API Football Leagues servisi.
    
    Bu servis mevcut lig ve kupa listesini almak için kullanılır.
    Lig ID'leri API genelinde benzersizdir ve tüm sezonlarda korunur.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        LeaguesService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/leagues'

    def fetch(self, **params) -> dict:
        """
        Fetch leagues data with given parameters.

        Args:
            **params: League query parameters

        Returns:
            dict: API response
        """
        return self.get_leagues(**params)

    def get_leagues(self, league_id: Optional[int] = None, name: Optional[str] = None,
                   country: Optional[str] = None, code: Optional[str] = None,
                   season: Optional[int] = None, team: Optional[int] = None,
                   league_type: Optional[str] = None, current: Optional[bool] = None,
                   search: Optional[str] = None, last: Optional[int] = None,
                   timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Lig listesini alır.
        
        Args:
            league_id (Optional[int]): Lig ID'si
            name (Optional[str]): Lig adı
            country (Optional[str]): Ülke adı
            code (Optional[str]): Ülke kodu (2-6 karakter, örn: FR, GB-ENG, IT)
            season (Optional[int]): Sezon (YYYY formatında)
            team (Optional[int]): Takım ID'si
            league_type (Optional[str]): Lig tipi ("league" veya "cup")
            current (Optional[bool]): Aktif sezonlar (True/False)
            search (Optional[str]): Arama terimi (minimum 3 karakter)
            last (Optional[int]): Son X lig/kupa (maksimum 2 karakter)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API response içeren lig listesi
            
        Example Response:
            {
                "get": "leagues",
                "parameters": {"id": "39"},
                "errors": [],
                "results": 1,
                "response": [
                    {
                        "league": {
                            "id": 39,
                            "name": "Premier League",
                            "type": "League",
                            "logo": "https://media.api-sports.io/football/leagues/2.png"
                        },
                        "country": {
                            "name": "England",
                            "code": "GB",
                            "flag": "https://media.api-sports.io/flags/gb.svg"
                        },
                        "seasons": [...]
                    }
                ]
            }
            
        Raises:
            APIFootballException: API hatası durumunda
            ValueError: Geçersiz parametre değerleri
            
        Usage:
            >>> leagues_service = LeaguesService()
            >>> result = leagues_service.get_leagues(league_id=39)
            >>> leagues = result['response']
        """
        params = {}
        
        if league_id is not None:
            params['id'] = league_id
        if name:
            params['name'] = name
        if country:
            params['country'] = country
        if code:
            if len(code) < 2 or len(code) > 6:
                raise ValueError("Country code must be between 2-6 characters")
            params['code'] = code
        if season is not None:
            if len(str(season)) != 4:
                raise ValueError("Season must be in YYYY format")
            params['season'] = season
        if team is not None:
            params['team'] = team
        if league_type:
            if league_type not in ['league', 'cup']:
                raise ValueError("League type must be 'league' or 'cup'")
            params['type'] = league_type
        if current is not None:
            params['current'] = 'true' if current else 'false'
        if search:
            if len(search) < 3:
                raise ValueError("Search parameter must be at least 3 characters long")
            params['search'] = search
        if last is not None:
            if last > 99:
                raise ValueError("Last parameter must be maximum 2 characters (99)")
            params['last'] = last
        
        return self.get(self.endpoint, params=params, timeout=timeout)
    
    def get_league_by_id(self, league_id: int, season: Optional[int] = None,
                        timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        ID'ye göre lig bilgisi alır.
        
        Args:
            league_id (int): Lig ID'si
            season (Optional[int]): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Lig bilgisi veya None
            
        Usage:
            >>> leagues_service = LeaguesService()
            >>> league = leagues_service.get_league_by_id(39, 2023)
            >>> if league:
            >>>     print(f"League: {league['league']['name']}")
        """
        result = self.get_leagues(league_id=league_id, season=season, timeout=timeout)
        leagues = result.get('response', [])
        return leagues[0] if leagues else None
    
    def get_leagues_by_country(self, country: str, season: Optional[int] = None,
                              timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Ülkeye göre lig listesi alır.
        
        Args:
            country (str): Ülke adı
            season (Optional[int]): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Lig listesi
            
        Usage:
            >>> leagues_service = LeaguesService()
            >>> leagues = leagues_service.get_leagues_by_country("England", 2023)
            >>> print(f"England leagues: {len(leagues)}")
        """
        result = self.get_leagues(country=country, season=season, timeout=timeout)
        return result.get('response', [])
    
    def get_current_leagues(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Aktif sezonları olan ligleri alır.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Aktif lig listesi
            
        Usage:
            >>> leagues_service = LeaguesService()
            >>> current_leagues = leagues_service.get_current_leagues()
            >>> print(f"Current leagues: {len(current_leagues)}")
        """
        result = self.get_leagues(current=True, timeout=timeout)
        return result.get('response', [])
    
    def search_leagues(self, search_term: str, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Lig listesinde arama yapar.
        
        Args:
            search_term (str): Arama terimi (minimum 3 karakter)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Arama sonucu lig listesi
            
        Usage:
            >>> leagues_service = LeaguesService()
            >>> leagues = leagues_service.search_leagues("premier")
            >>> print(f"Found leagues: {len(leagues)}")
        """
        result = self.get_leagues(search=search_term, timeout=timeout)
        return result.get('response', [])
    
    def get_leagues_by_type(self, league_type: str, country: Optional[str] = None,
                           timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Tipe göre lig listesi alır.
        
        Args:
            league_type (str): Lig tipi ("league" veya "cup")
            country (Optional[str]): Ülke adı (opsiyonel filtre)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Lig listesi
            
        Usage:
            >>> leagues_service = LeaguesService()
            >>> cups = leagues_service.get_leagues_by_type("cup", "England")
            >>> print(f"England cups: {len(cups)}")
        """
        result = self.get_leagues(league_type=league_type, country=country, timeout=timeout)
        return result.get('response', [])
    
    def get_team_leagues(self, team_id: int, season: Optional[int] = None,
                        timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Takımın katıldığı ligleri alır.
        
        Args:
            team_id (int): Takım ID'si
            season (Optional[int]): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Takımın katıldığı lig listesi
            
        Usage:
            >>> leagues_service = LeaguesService()
            >>> leagues = leagues_service.get_team_leagues(33, 2023)  # Manchester United
            >>> print(f"Team leagues: {len(leagues)}")
        """
        result = self.get_leagues(team=team_id, season=season, timeout=timeout)
        return result.get('response', [])
    
    def get_league_logo_url(self, league_id: int) -> str:
        """
        Lig logosu URL'ini oluşturur.
        
        Args:
            league_id (int): Lig ID'si
            
        Returns:
            str: Logo URL'i
            
        Usage:
            >>> leagues_service = LeaguesService()
            >>> logo_url = leagues_service.get_league_logo_url(39)
            >>> print(f"Logo URL: {logo_url}")
        """
        return f"https://media.api-sports.io/football/leagues/{league_id}.png"
    
    def get_league_coverage(self, league_id: int, season: Optional[int] = None,
                           timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Lig kapsamı bilgilerini alır (hangi verilerin mevcut olduğu).
        
        Args:
            league_id (int): Lig ID'si
            season (Optional[int]): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Kapsam bilgileri veya None
            
        Usage:
            >>> leagues_service = LeaguesService()
            >>> coverage = leagues_service.get_league_coverage(39, 2023)
            >>> if coverage:
            >>>     print(f"Has standings: {coverage.get('standings', False)}")
        """
        league = self.get_league_by_id(league_id, season, timeout)
        if not league or 'seasons' not in league:
            return None
        
        # En son sezonu bul veya belirtilen sezonu bul
        seasons = league['seasons']
        if not seasons:
            return None
        
        if season:
            for s in seasons:
                if s.get('year') == season:
                    return s.get('coverage')
        else:
            # En son sezonu al
            latest_season = max(seasons, key=lambda x: x.get('year', 0))
            return latest_season.get('coverage')
        
        return None
    
    def is_feature_available(self, league_id: int, feature: str, season: Optional[int] = None,
                           timeout: Optional[int] = None) -> bool:
        """
        Belirli bir özelliğin lig için mevcut olup olmadığını kontrol eder.
        
        Args:
            league_id (int): Lig ID'si
            feature (str): Özellik adı (örn: "standings", "players", "odds")
            season (Optional[int]): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            bool: Özellik mevcut ise True
            
        Usage:
            >>> leagues_service = LeaguesService()
            >>> has_standings = leagues_service.is_feature_available(39, "standings", 2023)
            >>> print(f"Has standings: {has_standings}")
        """
        coverage = self.get_league_coverage(league_id, season, timeout)
        if not coverage:
            return False
        
        # Nested feature kontrolü (örn: fixtures.events)
        if '.' in feature:
            parts = feature.split('.')
            current = coverage
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return False
            return bool(current)
        else:
            return bool(coverage.get(feature, False))


# Convenience functions
def get_popular_leagues(config: Optional[APIConfig] = None) -> List[Dict[str, Any]]:
    """
    Popüler ligleri almak için convenience function.
    
    Args:
        config (Optional[APIConfig]): API konfigürasyonu
        
    Returns:
        List[Dict[str, Any]]: Popüler lig listesi
    """
    popular_league_ids = [39, 140, 78, 135, 61, 2, 3, 71, 94, 88]  # Premier League, La Liga, etc.
    
    with LeaguesService(config) as service:
        leagues = []
        for league_id in popular_league_ids:
            try:
                league = service.get_league_by_id(league_id)
                if league:
                    leagues.append(league)
            except Exception:
                continue
        return leagues


def find_league(name: str, config: Optional[APIConfig] = None) -> Optional[Dict[str, Any]]:
    """
    Lig bulmak için convenience function.
    
    Args:
        name (str): Lig adı
        config (Optional[APIConfig]): API konfigürasyonu
        
    Returns:
        Optional[Dict[str, Any]]: Lig bilgisi
    """
    with LeaguesService(config) as service:
        leagues = service.search_leagues(name)
        return leagues[0] if leagues else None


if __name__ == "__main__":
    # Test leagues service
    print("Testing Leagues Service...")
    
    try:
        with LeaguesService() as service:
            # Test get league by ID
            premier_league = service.get_league_by_id(39)
            if premier_league:
                print(f"✓ Premier League found: {premier_league['league']['name']}")
            
            # Test search
            search_results = service.search_leagues("premier")
            print(f"✓ Search 'premier' found: {len(search_results)} leagues")
            
            # Test current leagues
            current_leagues = service.get_current_leagues()
            print(f"✓ Current leagues: {len(current_leagues)}")
            
            # Test logo URL
            logo_url = service.get_league_logo_url(39)
            print(f"✓ Logo URL: {logo_url}")
            
            # Test coverage
            coverage = service.get_league_coverage(39)
            if coverage:
                print(f"✓ Premier League has standings: {coverage.get('standings', False)}")
            
    except Exception as e:
        print(f"✗ Leagues service test failed: {e}")
