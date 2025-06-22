"""
API Football Fixtures Round Service

Bu servis API Football'dan belirli bir round'daki maçları almak için kullanılır.
Sistem prompt'ta belirtilen fixtures_round_service.py implementasyonu.

Author: Footy-Brain Team
Version: 1.0.0
"""

from typing import Dict, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class FixturesRoundService(BaseService):
    """
    API Football Fixtures Round servisi.
    
    Bu servis belirli bir round'daki maçları almak için kullanılır.
    /fixtures endpoint'ini round parametresi ile kullanır.
    
    Usage:
        >>> round_service = FixturesRoundService()
        >>> result = round_service.fetch(league=39, season=2023, round="Regular Season - 1")
        >>> print(f"Found {result['results']} fixtures")
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        FixturesRoundService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/fixtures'
        
    def fetch(self, **params) -> Dict[str, Any]:
        """
        Belirli bir round'daki maçları getirir.
        
        Args:
            **params: Endpoint parametreleri
                - league (int): Lig ID'si (zorunlu)
                - season (int): Sezon yılı (zorunlu)
                - round (str): Round adı (zorunlu)
                - team (int): Takım ID'si (opsiyonel)
                - date (str): Tarih (YYYY-MM-DD)
                - timezone (str): Zaman dilimi
                
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            ValueError: Gerekli parametreler eksikse
            
        Usage:
            >>> service = FixturesRoundService()
            >>> # Premier League 1. hafta maçları
            >>> fixtures = service.fetch(
            ...     league=39, 
            ...     season=2023, 
            ...     round="Regular Season - 1"
            ... )
            >>> # Belirli takımın round maçları
            >>> team_fixtures = service.fetch(
            ...     league=39, 
            ...     season=2023, 
            ...     round="Regular Season - 1",
            ...     team=33
            ... )
        """
        # Parametre validasyonu
        validated_params = self._validate_params(params)
        
        # API çağrısı
        response = self.get(self.endpoint, params=validated_params)
        
        return response
    
    def _validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fixtures round endpoint parametrelerini doğrular.
        
        Args:
            params (Dict[str, Any]): Gelen parametreler
            
        Returns:
            Dict[str, Any]: Doğrulanmış parametreler
            
        Raises:
            ValueError: Geçersiz veya eksik parametre durumunda
        """
        validated = {}
        
        # League parametresi (zorunlu)
        if 'league' not in params:
            raise ValueError("League parametresi zorunludur")
        
        league_id = params['league']
        if isinstance(league_id, (int, str)):
            try:
                validated['league'] = int(league_id)
            except ValueError:
                raise ValueError(f"Geçersiz lig ID: {league_id}")
        else:
            raise ValueError("Lig ID integer olmalıdır")
        
        # Season parametresi (zorunlu)
        if 'season' not in params:
            raise ValueError("Season parametresi zorunludur")
        
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
        
        # Round parametresi (zorunlu)
        if 'round' not in params:
            raise ValueError("Round parametresi zorunludur")
        
        round_name = params['round']
        if isinstance(round_name, str) and round_name.strip():
            validated['round'] = round_name.strip()
        else:
            raise ValueError("Round adı boş olmayan string olmalıdır")
        
        # Team parametresi (opsiyonel)
        if 'team' in params:
            team_id = params['team']
            if isinstance(team_id, (int, str)):
                try:
                    validated['team'] = int(team_id)
                except ValueError:
                    raise ValueError(f"Geçersiz takım ID: {team_id}")
            else:
                raise ValueError("Takım ID integer olmalıdır")
        
        # Date parametresi (opsiyonel)
        if 'date' in params:
            date = params['date']
            if isinstance(date, str) and date.strip():
                # Basit tarih formatı kontrolü (YYYY-MM-DD)
                date_str = date.strip()
                if len(date_str) == 10 and date_str.count('-') == 2:
                    try:
                        year, month, day = date_str.split('-')
                        int(year), int(month), int(day)
                        validated['date'] = date_str
                    except ValueError:
                        raise ValueError(f"Geçersiz tarih formatı: {date}. YYYY-MM-DD formatında olmalıdır")
                else:
                    raise ValueError(f"Geçersiz tarih formatı: {date}. YYYY-MM-DD formatında olmalıdır")
            else:
                raise ValueError("Tarih string olmalıdır")
        
        # Timezone parametresi (opsiyonel)
        if 'timezone' in params:
            timezone = params['timezone']
            if isinstance(timezone, str) and timezone.strip():
                validated['timezone'] = timezone.strip()
            else:
                raise ValueError("Timezone string olmalıdır")
        
        return validated
    
    def get_round_fixtures(self, league_id: int, season: int, round_name: str, 
                          team_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Belirli bir round'daki maçları getirir.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon yılı
            round_name (str): Round adı
            team_id (Optional[int]): Takım ID'si (opsiyonel)
            
        Returns:
            Dict[str, Any]: API yanıtı
        """
        params = {
            'league': league_id,
            'season': season,
            'round': round_name
        }
        
        if team_id:
            params['team'] = team_id
        
        return self.fetch(**params)
    
    def get_team_round_fixtures(self, league_id: int, season: int, 
                               round_name: str, team_id: int) -> Dict[str, Any]:
        """
        Belirli bir takımın round'daki maçlarını getirir.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon yılı
            round_name (str): Round adı
            team_id (int): Takım ID'si
            
        Returns:
            Dict[str, Any]: API yanıtı
        """
        return self.get_round_fixtures(league_id, season, round_name, team_id)
    
    def get_round_fixtures_by_date(self, league_id: int, season: int, 
                                  round_name: str, date: str) -> Dict[str, Any]:
        """
        Belirli bir tarihteki round maçlarını getirir.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon yılı
            round_name (str): Round adı
            date (str): Tarih (YYYY-MM-DD)
            
        Returns:
            Dict[str, Any]: API yanıtı
        """
        params = {
            'league': league_id,
            'season': season,
            'round': round_name,
            'date': date
        }
        
        return self.fetch(**params)


# Convenience function
def get_round_fixtures(league_id: int, season: int, round_name: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function for getting round fixtures.
    
    Args:
        league_id (int): League ID
        season (int): Season year
        round_name (str): Round name
        **kwargs: Additional parameters
        
    Returns:
        Dict[str, Any]: API response
    """
    service = FixturesRoundService()
    try:
        params = {
            'league': league_id,
            'season': season,
            'round': round_name,
            **kwargs
        }
        return service.fetch(**params)
    finally:
        service.close()
