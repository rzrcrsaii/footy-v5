"""
API Football Teams Service Module

Bu modül API Football Teams endpoint'i için servis sınıfını içerir.
Takım bilgilerini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class TeamsService(BaseService):
    """
    API Football Teams servisi.
    
    Bu servis takım bilgilerini almak için kullanılır.
    Takım ID'leri API genelinde benzersizdir ve tüm lig/kupa katılımlarında korunur.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        TeamsService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/teams'

    def fetch(self, **params) -> dict:
        """
        Fetch data with given parameters.
        
        Args:
            **params: Query parameters
            
        Returns:
            dict: API response
        """
        # Use the first public method that starts with 'get_'
        for attr_name in dir(self):
            if attr_name.startswith('get_') and not attr_name.startswith('get_config'):
                method = getattr(self, attr_name)
                if callable(method):
                    try:
                        return method(**params)
                    except TypeError:
                        # If method doesn't accept **params, try without params
                        return method()
        
        # Fallback to base implementation
        return super().fetch(**params)

    
    def get_teams(self, team_id: Optional[int] = None,
                 name: Optional[str] = None,
                 league: Optional[int] = None,
                 season: Optional[int] = None,
                 country: Optional[str] = None,
                 code: Optional[str] = None,
                 venue: Optional[int] = None,
                 search: Optional[str] = None,
                 timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Takım bilgilerini alır.
        
        Args:
            team_id (Optional[int]): Takım ID'si
            name (Optional[str]): Takım adı
            league (Optional[int]): Lig ID'si
            season (Optional[int]): Sezon (YYYY formatında)
            country (Optional[str]): Ülke adı
            code (Optional[str]): Takım kodu (3 karakter)
            venue (Optional[int]): Saha ID'si
            search (Optional[str]): Arama terimi (min 3 karakter)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            ValueError: Hiç parametre verilmezse veya search 3 karakterden kısaysa
            
        Usage:
            >>> teams_service = TeamsService()
            >>> result = teams_service.get_teams(team_id=33)
            >>> print(f"Teams found: {result['results']}")
        """
        params = {}
        
        # En az bir parametre gerekli
        if not any([team_id, name, league, country, code, venue, search]):
            raise ValueError("At least one parameter is required")
        
        if team_id is not None:
            params['id'] = team_id
        
        if name is not None:
            params['name'] = name
        
        if league is not None:
            params['league'] = league
        
        if season is not None:
            params['season'] = season
        
        if country is not None:
            params['country'] = country
        
        if code is not None:
            if len(code) != 3:
                raise ValueError("Team code must be exactly 3 characters")
            params['code'] = code
        
        if venue is not None:
            params['venue'] = venue
        
        if search is not None:
            if len(search) < 3:
                raise ValueError("Search term must be at least 3 characters")
            params['search'] = search
        
        return self.get(
            endpoint=self.endpoint,
            params=params,
            timeout=timeout
        )
    
    def get_team_by_id(self, team_id: int, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir takımın detaylarını alır.
        
        Args:
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Takım detayları, bulunamazsa None
            
        Usage:
            >>> teams_service = TeamsService()
            >>> team = teams_service.get_team_by_id(33)
            >>> if team:
            ...     print(f"Team: {team['team']['name']}")
        """
        result = self.get_teams(team_id=team_id, timeout=timeout)
        teams = result.get('response', [])
        return teams[0] if teams else None
    
    def get_teams_by_league(self, league_id: int, season: int,
                           timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir lig ve sezondaki takımları alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Takım listesi
            
        Usage:
            >>> teams_service = TeamsService()
            >>> teams = teams_service.get_teams_by_league(39, 2023)
            >>> print(f"Premier League teams: {len(teams)}")
        """
        result = self.get_teams(league=league_id, season=season, timeout=timeout)
        return result.get('response', [])
    
    def get_teams_by_country(self, country: str, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir ülkedeki takımları alır.
        
        Args:
            country (str): Ülke adı
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Takım listesi
            
        Usage:
            >>> teams_service = TeamsService()
            >>> teams = teams_service.get_teams_by_country("England")
            >>> print(f"English teams: {len(teams)}")
        """
        result = self.get_teams(country=country, timeout=timeout)
        return result.get('response', [])
    
    def search_teams(self, search_term: str, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Takım arar.
        
        Args:
            search_term (str): Arama terimi (min 3 karakter)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Bulunan takımlar
            
        Usage:
            >>> teams_service = TeamsService()
            >>> teams = teams_service.search_teams("manchester")
            >>> print(f"Manchester teams: {len(teams)}")
        """
        result = self.get_teams(search=search_term, timeout=timeout)
        return result.get('response', [])
    
    def get_team_by_name(self, team_name: str, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Takım adına göre takım arar.
        
        Args:
            team_name (str): Takım adı
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Takım detayları, bulunamazsa None
            
        Usage:
            >>> teams_service = TeamsService()
            >>> team = teams_service.get_team_by_name("Manchester United")
            >>> if team:
            ...     print(f"Team ID: {team['team']['id']}")
        """
        result = self.get_teams(name=team_name, timeout=timeout)
        teams = result.get('response', [])
        return teams[0] if teams else None
    
    def get_team_logo_url(self, team_id: int) -> str:
        """
        Takım logosu URL'ini oluşturur.
        
        Args:
            team_id (int): Takım ID'si
            
        Returns:
            str: Logo URL'i
            
        Usage:
            >>> teams_service = TeamsService()
            >>> logo_url = teams_service.get_team_logo_url(33)
            >>> print(f"Logo URL: {logo_url}")
        """
        return f"https://media.api-sports.io/football/teams/{team_id}.png"
    
    def get_team_venue(self, team_id: int, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Takımın stadyum bilgilerini alır.
        
        Args:
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Stadyum bilgileri, bulunamazsa None
            
        Usage:
            >>> teams_service = TeamsService()
            >>> venue = teams_service.get_team_venue(33)
            >>> if venue:
            ...     print(f"Stadium: {venue['name']} (Capacity: {venue['capacity']})")
        """
        team_data = self.get_team_by_id(team_id, timeout=timeout)
        return team_data.get('venue') if team_data else None
    
    def is_national_team(self, team_id: int, timeout: Optional[int] = None) -> bool:
        """
        Takımın milli takım olup olmadığını kontrol eder.
        
        Args:
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            bool: Milli takım ise True, değilse False
            
        Usage:
            >>> teams_service = TeamsService()
            >>> is_national = teams_service.is_national_team(33)
            >>> print(f"Manchester United is national team: {is_national}")
        """
        team_data = self.get_team_by_id(team_id, timeout=timeout)
        if team_data:
            return team_data.get('team', {}).get('national', False)
        return False
    
    def get_team_founded_year(self, team_id: int, timeout: Optional[int] = None) -> Optional[int]:
        """
        Takımın kuruluş yılını döndürür.
        
        Args:
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[int]: Kuruluş yılı, bulunamazsa None
            
        Usage:
            >>> teams_service = TeamsService()
            >>> founded = teams_service.get_team_founded_year(33)
            >>> print(f"Manchester United founded: {founded}")
        """
        team_data = self.get_team_by_id(team_id, timeout=timeout)
        if team_data:
            return team_data.get('team', {}).get('founded')
        return None


if __name__ == "__main__":
    # Test teams service
    print("Testing Teams Service...")
    
    try:
        with TeamsService() as service:
            # Test get team by ID
            team = service.get_team_by_id(33)
            if team:
                print(f"✓ Team found: {team['team']['name']}")
            
            # Test get teams by league
            teams = service.get_teams_by_league(39, 2023)
            print(f"✓ Premier League teams: {len(teams)}")
            
            # Test search teams
            search_results = service.search_teams("manchester")
            print(f"✓ Manchester teams found: {len(search_results)}")
            
            # Test get team venue
            venue = service.get_team_venue(33)
            if venue:
                print(f"✓ Stadium: {venue['name']} (Capacity: {venue['capacity']})")
            
            # Test logo URL
            logo_url = service.get_team_logo_url(33)
            print(f"✓ Logo URL: {logo_url}")
            
            # Test founded year
            founded = service.get_team_founded_year(33)
            print(f"✓ Manchester United founded: {founded}")
            
    except Exception as e:
        print(f"✗ Error testing teams service: {e}")
