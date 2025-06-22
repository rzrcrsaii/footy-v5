"""
API Football Teams Info Service

Bu servis API Football'dan takım bilgilerini almak için kullanılır.
Sistem prompt'ta belirtilen teamsinfo_service.py implementasyonu.

Author: Footy-Brain Team
Version: 1.0.0
"""

from typing import Dict, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class TeamsInfoService(BaseService):
    """
    API Football Teams Info servisi.
    
    Bu servis takım bilgilerini almak için kullanılır.
    /teams endpoint'ini kullanır.
    
    Usage:
        >>> teams_service = TeamsInfoService()
        >>> result = teams_service.fetch(league=39, season=2023)
        >>> print(f"Found {result['results']} teams")
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        TeamsInfoService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/teams'
        
    def fetch(self, **params) -> Dict[str, Any]:
        """
        Takım bilgilerini getirir.
        
        Args:
            **params: Endpoint parametreleri
                - id (int): Takım ID'si
                - name (str): Takım adı
                - league (int): Lig ID'si
                - season (int): Sezon yılı
                - country (str): Ülke adı
                - code (str): Ülke kodu
                - venue (int): Venue ID'si
                - search (str): Arama terimi
                
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> service = TeamsInfoService()
            >>> # Tüm takımları getir
            >>> all_teams = service.fetch()
            >>> # Premier League takımları
            >>> pl_teams = service.fetch(league=39, season=2023)
            >>> # Belirli bir takım
            >>> man_utd = service.fetch(id=33)
            >>> # İngiltere takımları
            >>> england_teams = service.fetch(country="England")
        """
        # Parametre validasyonu
        validated_params = self._validate_params(params)
        
        # API çağrısı
        response = self.get(self.endpoint, params=validated_params)
        
        return response
    
    def _validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Teams endpoint parametrelerini doğrular.
        
        Args:
            params (Dict[str, Any]): Gelen parametreler
            
        Returns:
            Dict[str, Any]: Doğrulanmış parametreler
            
        Raises:
            ValueError: Geçersiz parametre durumunda
        """
        validated = {}
        
        # ID parametresi
        if 'id' in params:
            team_id = params['id']
            if isinstance(team_id, (int, str)):
                try:
                    validated['id'] = int(team_id)
                except ValueError:
                    raise ValueError(f"Geçersiz takım ID: {team_id}")
            else:
                raise ValueError("Takım ID integer olmalıdır")
        
        # Name parametresi
        if 'name' in params:
            name = params['name']
            if isinstance(name, str) and name.strip():
                validated['name'] = name.strip()
            else:
                raise ValueError("Takım adı boş olmayan string olmalıdır")
        
        # League parametresi
        if 'league' in params:
            league_id = params['league']
            if isinstance(league_id, (int, str)):
                try:
                    validated['league'] = int(league_id)
                except ValueError:
                    raise ValueError(f"Geçersiz lig ID: {league_id}")
            else:
                raise ValueError("Lig ID integer olmalıdır")
        
        # Season parametresi
        if 'season' in params:
            season = params['season']
            if isinstance(season, (int, str)):
                try:
                    season_int = int(season)
                    if 1900 <= season_int <= 2100:
                        validated['season'] = season_int
                    else:
                        raise ValueError("Sezon 1900-2100 arasında olmalıdır")
                except ValueError:
                    raise ValueError(f"Geçersiz sezon: {season}")
            else:
                raise ValueError("Sezon integer olmalıdır")
        
        # Country parametresi
        if 'country' in params:
            country = params['country']
            if isinstance(country, str) and country.strip():
                validated['country'] = country.strip()
            else:
                raise ValueError("Ülke adı boş olmayan string olmalıdır")
        
        # Code parametresi
        if 'code' in params:
            code = params['code']
            if isinstance(code, str) and len(code.strip()) in [2, 3]:
                validated['code'] = code.strip().upper()
            else:
                raise ValueError("Ülke kodu 2 veya 3 karakter olmalıdır")
        
        # Venue parametresi
        if 'venue' in params:
            venue_id = params['venue']
            if isinstance(venue_id, (int, str)):
                try:
                    validated['venue'] = int(venue_id)
                except ValueError:
                    raise ValueError(f"Geçersiz venue ID: {venue_id}")
            else:
                raise ValueError("Venue ID integer olmalıdır")
        
        # Search parametresi
        if 'search' in params:
            search = params['search']
            if isinstance(search, str) and len(search.strip()) >= 2:
                validated['search'] = search.strip()
            else:
                raise ValueError("Arama terimi en az 2 karakter olmalıdır")
        
        return validated
    
    def get_team_by_id(self, team_id: int) -> Dict[str, Any]:
        """
        Belirli bir takımı ID ile getirir.
        
        Args:
            team_id (int): Takım ID'si
            
        Returns:
            Dict[str, Any]: API yanıtı
        """
        return self.fetch(id=team_id)
    
    def get_teams_by_league(self, league_id: int, season: int) -> Dict[str, Any]:
        """
        Belirli bir ligdeki takımları getirir.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon yılı
            
        Returns:
            Dict[str, Any]: API yanıtı
        """
        return self.fetch(league=league_id, season=season)
    
    def get_teams_by_country(self, country: str) -> Dict[str, Any]:
        """
        Belirli bir ülkedeki takımları getirir.
        
        Args:
            country (str): Ülke adı
            
        Returns:
            Dict[str, Any]: API yanıtı
        """
        return self.fetch(country=country)
    
    def search_teams(self, search_term: str) -> Dict[str, Any]:
        """
        Takım adında arama yapar.
        
        Args:
            search_term (str): Arama terimi
            
        Returns:
            Dict[str, Any]: API yanıtı
        """
        return self.fetch(search=search_term)
    
    def get_teams_by_venue(self, venue_id: int) -> Dict[str, Any]:
        """
        Belirli bir venue'deki takımları getirir.
        
        Args:
            venue_id (int): Venue ID'si
            
        Returns:
            Dict[str, Any]: API yanıtı
        """
        return self.fetch(venue=venue_id)


# Convenience functions
def get_team_info(team_id: int) -> Dict[str, Any]:
    """
    Convenience function for getting team info by ID.
    
    Args:
        team_id (int): Team ID
        
    Returns:
        Dict[str, Any]: API response
    """
    service = TeamsInfoService()
    try:
        return service.get_team_by_id(team_id)
    finally:
        service.close()


def get_league_teams(league_id: int, season: int) -> Dict[str, Any]:
    """
    Convenience function for getting teams in a league.
    
    Args:
        league_id (int): League ID
        season (int): Season year
        
    Returns:
        Dict[str, Any]: API response
    """
    service = TeamsInfoService()
    try:
        return service.get_teams_by_league(league_id, season)
    finally:
        service.close()


def search_teams_by_name(search_term: str) -> Dict[str, Any]:
    """
    Convenience function for searching teams by name.
    
    Args:
        search_term (str): Search term
        
    Returns:
        Dict[str, Any]: API response
    """
    service = TeamsInfoService()
    try:
        return service.search_teams(search_term)
    finally:
        service.close()
