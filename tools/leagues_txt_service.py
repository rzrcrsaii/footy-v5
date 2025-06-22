"""
API Football Leagues Service

Bu servis API Football'dan lig bilgilerini almak için kullanılır.
Sistem prompt'ta belirtilen leagues_txt_service.py implementasyonu.

Author: Footy-Brain Team
Version: 1.0.0
"""

from typing import Dict, Any, Optional, List
from .base_service import BaseService
from .api_config import APIConfig


class LeaguesTxtService(BaseService):
    """
    API Football Leagues servisi.
    
    Bu servis lig bilgilerini almak için kullanılır.
    /leagues endpoint'ini kullanır.
    
    Usage:
        >>> leagues_service = LeaguesTxtService()
        >>> result = leagues_service.fetch(country="England")
        >>> print(f"Found {result['results']} leagues")
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        LeaguesTxtService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/leagues'
        
    def fetch(self, **params) -> Dict[str, Any]:
        """
        Lig bilgilerini getirir.
        
        Args:
            **params: Endpoint parametreleri
                - id (int): Lig ID'si
                - name (str): Lig adı
                - country (str): Ülke adı
                - code (str): Ülke kodu
                - season (int): Sezon yılı
                - team (int): Takım ID'si
                - type (str): Lig tipi (league, cup)
                - current (str): Mevcut sezon (true/false)
                - search (str): Arama terimi
                - last (int): Son N lig
                
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> service = LeaguesTxtService()
            >>> # Tüm ligleri getir
            >>> all_leagues = service.fetch()
            >>> # İngiltere liglerini getir
            >>> england_leagues = service.fetch(country="England")
            >>> # Belirli bir ligi getir
            >>> premier_league = service.fetch(id=39)
            >>> # Mevcut sezon liglerini getir
            >>> current_leagues = service.fetch(current="true")
        """
        # Parametre validasyonu
        validated_params = self._validate_params(params)
        
        # API çağrısı
        response = self.get(self.endpoint, params=validated_params)
        
        return response
    
    def _validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Leagues endpoint parametrelerini doğrular.
        
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
            league_id = params['id']
            if isinstance(league_id, (int, str)):
                try:
                    validated['id'] = int(league_id)
                except ValueError:
                    raise ValueError(f"Geçersiz lig ID: {league_id}")
            else:
                raise ValueError("Lig ID integer olmalıdır")
        
        # Name parametresi
        if 'name' in params:
            name = params['name']
            if isinstance(name, str) and name.strip():
                validated['name'] = name.strip()
            else:
                raise ValueError("Lig adı boş olmayan string olmalıdır")
        
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
        
        # Team parametresi
        if 'team' in params:
            team_id = params['team']
            if isinstance(team_id, (int, str)):
                try:
                    validated['team'] = int(team_id)
                except ValueError:
                    raise ValueError(f"Geçersiz takım ID: {team_id}")
            else:
                raise ValueError("Takım ID integer olmalıdır")
        
        # Type parametresi
        if 'type' in params:
            league_type = params['type']
            valid_types = ['league', 'cup']
            if isinstance(league_type, str) and league_type.lower() in valid_types:
                validated['type'] = league_type.lower()
            else:
                raise ValueError(f"Lig tipi {valid_types} değerlerinden biri olmalıdır")
        
        # Current parametresi
        if 'current' in params:
            current = params['current']
            if isinstance(current, (bool, str)):
                if isinstance(current, bool):
                    validated['current'] = 'true' if current else 'false'
                elif current.lower() in ['true', 'false']:
                    validated['current'] = current.lower()
                else:
                    raise ValueError("Current parametresi true/false olmalıdır")
            else:
                raise ValueError("Current parametresi boolean veya string olmalıdır")
        
        # Search parametresi
        if 'search' in params:
            search = params['search']
            if isinstance(search, str) and len(search.strip()) >= 2:
                validated['search'] = search.strip()
            else:
                raise ValueError("Arama terimi en az 2 karakter olmalıdır")
        
        # Last parametresi
        if 'last' in params:
            last = params['last']
            if isinstance(last, (int, str)):
                try:
                    last_int = int(last)
                    if 1 <= last_int <= 100:
                        validated['last'] = last_int
                    else:
                        raise ValueError("Last parametresi 1-100 arasında olmalıdır")
                except ValueError:
                    raise ValueError(f"Geçersiz last değeri: {last}")
            else:
                raise ValueError("Last parametresi integer olmalıdır")
        
        return validated
    
    def get_leagues_by_country(self, country: str, season: Optional[int] = None) -> Dict[str, Any]:
        """
        Belirli bir ülkenin liglerini getirir.
        
        Args:
            country (str): Ülke adı
            season (Optional[int]): Sezon yılı
            
        Returns:
            Dict[str, Any]: API yanıtı
        """
        params = {'country': country}
        if season:
            params['season'] = season
        
        return self.fetch(**params)
    
    def get_league_by_id(self, league_id: int, season: Optional[int] = None) -> Dict[str, Any]:
        """
        Belirli bir ligi ID ile getirir.
        
        Args:
            league_id (int): Lig ID'si
            season (Optional[int]): Sezon yılı
            
        Returns:
            Dict[str, Any]: API yanıtı
        """
        params = {'id': league_id}
        if season:
            params['season'] = season
        
        return self.fetch(**params)
    
    def get_current_leagues(self) -> Dict[str, Any]:
        """
        Mevcut sezon liglerini getirir.
        
        Returns:
            Dict[str, Any]: API yanıtı
        """
        return self.fetch(current='true')
    
    def search_leagues(self, search_term: str) -> Dict[str, Any]:
        """
        Lig adında arama yapar.
        
        Args:
            search_term (str): Arama terimi
            
        Returns:
            Dict[str, Any]: API yanıtı
        """
        return self.fetch(search=search_term)


# Convenience function
def get_leagues(**params) -> Dict[str, Any]:
    """
    Convenience function for getting leagues.
    
    Args:
        **params: League parameters
        
    Returns:
        Dict[str, Any]: API response
    """
    service = LeaguesTxtService()
    try:
        return service.fetch(**params)
    finally:
        service.close()
