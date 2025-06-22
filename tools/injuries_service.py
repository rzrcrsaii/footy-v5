"""
API Football Injuries Service Module

Bu modül API Football Injuries endpoint'i için servis sınıfını içerir.
Oyuncu sakatlık ve ceza durumlarını almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
from .base_service import BaseService
from .api_config import APIConfig


class InjuriesService(BaseService):
    """
    API Football Injuries servisi.
    
    Bu servis oyuncu sakatlık ve ceza durumlarını almak için kullanılır.
    Nisan 2021'den itibaren veri mevcuttur.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        InjuriesService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/injuries'

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

    
    def get_injuries(self, league: Optional[int] = None,
                    season: Optional[int] = None,
                    fixture: Optional[int] = None,
                    team: Optional[int] = None,
                    player: Optional[int] = None,
                    date: Optional[Union[str, date]] = None,
                    fixture_ids: Optional[List[int]] = None,
                    timezone: Optional[str] = None,
                    timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Sakatlık ve ceza durumlarını alır.
        
        Args:
            league (Optional[int]): Lig ID'si
            season (Optional[int]): Sezon (YYYY formatında)
            fixture (Optional[int]): Maç ID'si
            team (Optional[int]): Takım ID'si
            player (Optional[int]): Oyuncu ID'si
            date (Optional[Union[str, date]]): Tarih (YYYY-MM-DD)
            fixture_ids (Optional[List[int]]): Maç ID'leri listesi (max 20)
            timezone (Optional[str]): Zaman dilimi
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            ValueError: Hiç parametre verilmezse
            
        Usage:
            >>> injuries_service = InjuriesService()
            >>> result = injuries_service.get_injuries(fixture=686314)
            >>> print(f"Injuries found: {result['results']}")
        """
        params = {}
        
        # En az bir parametre gerekli
        if not any([league, fixture, team, player, date, fixture_ids]):
            raise ValueError("At least one parameter is required")
        
        if league is not None:
            params['league'] = league
        
        if season is not None:
            params['season'] = season
        
        if fixture is not None:
            params['fixture'] = fixture
        
        if team is not None:
            params['team'] = team
        
        if player is not None:
            params['player'] = player
        
        if date is not None:
            if isinstance(date, datetime):
                params['date'] = date.strftime('%Y-%m-%d')
            elif isinstance(date, str):
                params['date'] = date
        
        if fixture_ids:
            if len(fixture_ids) > 20:
                raise ValueError("Maximum 20 fixture IDs allowed")
            params['ids'] = '-'.join(map(str, fixture_ids))
        
        if timezone is not None:
            params['timezone'] = timezone
        
        return self.get(
            endpoint=self.endpoint,
            params=params,
            timeout=timeout
        )
    
    def get_fixture_injuries(self, fixture_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir maçın sakatlık durumlarını alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Sakatlık listesi
            
        Usage:
            >>> injuries_service = InjuriesService()
            >>> injuries = injuries_service.get_fixture_injuries(686314)
            >>> print(f"Injured players: {len(injuries)}")
        """
        result = self.get_injuries(fixture=fixture_id, timeout=timeout)
        return result.get('response', [])
    
    def get_team_injuries(self, team_id: int, season: int, league: Optional[int] = None,
                         timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Takımın sakatlık durumlarını alır.
        
        Args:
            team_id (int): Takım ID'si
            season (int): Sezon (YYYY formatında)
            league (Optional[int]): Lig ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Takım sakatlık listesi
            
        Usage:
            >>> injuries_service = InjuriesService()
            >>> injuries = injuries_service.get_team_injuries(157, 2021)
            >>> print(f"Bayern Munich injuries: {len(injuries)}")
        """
        result = self.get_injuries(team=team_id, season=season, league=league, timeout=timeout)
        return result.get('response', [])
    
    def get_player_injuries(self, player_id: int, season: int,
                           timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Oyuncunun sakatlık geçmişini alır.
        
        Args:
            player_id (int): Oyuncu ID'si
            season (int): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Oyuncu sakatlık geçmişi
            
        Usage:
            >>> injuries_service = InjuriesService()
            >>> injuries = injuries_service.get_player_injuries(521, 2021)
            >>> print(f"Lewandowski injuries: {len(injuries)}")
        """
        result = self.get_injuries(player=player_id, season=season, timeout=timeout)
        return result.get('response', [])
    
    def get_league_injuries(self, league_id: int, season: int,
                           timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Ligin sakatlık durumlarını alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Lig sakatlık listesi
            
        Usage:
            >>> injuries_service = InjuriesService()
            >>> injuries = injuries_service.get_league_injuries(39, 2023)
            >>> print(f"Premier League injuries: {len(injuries)}")
        """
        result = self.get_injuries(league=league_id, season=season, timeout=timeout)
        return result.get('response', [])
    
    def get_injuries_by_date(self, injury_date: Union[str, date],
                            timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir tarihteki sakatlık durumlarını alır.
        
        Args:
            injury_date (Union[str, date]): Tarih (YYYY-MM-DD formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Tarih bazlı sakatlık listesi
            
        Usage:
            >>> injuries_service = InjuriesService()
            >>> injuries = injuries_service.get_injuries_by_date("2021-04-07")
            >>> print(f"Injuries on date: {len(injuries)}")
        """
        result = self.get_injuries(date=injury_date, timeout=timeout)
        return result.get('response', [])
    
    def get_missing_players(self, fixture_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Maçta oynamayacak oyuncuları alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Oynamayacak oyuncular
            
        Usage:
            >>> injuries_service = InjuriesService()
            >>> missing = injuries_service.get_missing_players(686314)
            >>> print(f"Missing players: {len(missing)}")
        """
        injuries = self.get_fixture_injuries(fixture_id, timeout=timeout)
        return [injury for injury in injuries 
                if injury.get('player', {}).get('type') == 'Missing Fixture']
    
    def get_questionable_players(self, fixture_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Maçta oynama durumu belirsiz oyuncuları alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Durumu belirsiz oyuncular
            
        Usage:
            >>> injuries_service = InjuriesService()
            >>> questionable = injuries_service.get_questionable_players(686314)
            >>> print(f"Questionable players: {len(questionable)}")
        """
        injuries = self.get_fixture_injuries(fixture_id, timeout=timeout)
        return [injury for injury in injuries 
                if injury.get('player', {}).get('type') == 'Questionable']
    
    def get_injuries_by_reason(self, fixture_id: int, reason: str,
                              timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir sebepten dolayı oynamayan oyuncuları alır.
        
        Args:
            fixture_id (int): Maç ID'si
            reason (str): Sakatlık sebebi (örn: "Knee Injury", "Suspended")
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Belirtilen sebepten oynamayan oyuncular
            
        Usage:
            >>> injuries_service = InjuriesService()
            >>> knee_injuries = injuries_service.get_injuries_by_reason(686314, "Knee Injury")
            >>> print(f"Knee injuries: {len(knee_injuries)}")
        """
        injuries = self.get_fixture_injuries(fixture_id, timeout=timeout)
        return [injury for injury in injuries 
                if reason.lower() in injury.get('player', {}).get('reason', '').lower()]
    
    def get_suspended_players(self, fixture_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Cezalı oyuncuları alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Cezalı oyuncular
            
        Usage:
            >>> injuries_service = InjuriesService()
            >>> suspended = injuries_service.get_suspended_players(686314)
            >>> print(f"Suspended players: {len(suspended)}")
        """
        return self.get_injuries_by_reason(fixture_id, "Suspended", timeout=timeout)
    
    def get_team_injury_statistics(self, team_id: int, season: int,
                                  timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Takımın sakatlık istatistiklerini hesaplar.
        
        Args:
            team_id (int): Takım ID'si
            season (int): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: Sakatlık istatistikleri
            
        Usage:
            >>> injuries_service = InjuriesService()
            >>> stats = injuries_service.get_team_injury_statistics(157, 2021)
            >>> print(f"Total injuries: {stats['total_injuries']}")
        """
        injuries = self.get_team_injuries(team_id, season, timeout=timeout)
        
        total_injuries = len(injuries)
        missing_fixtures = len([i for i in injuries 
                               if i.get('player', {}).get('type') == 'Missing Fixture'])
        questionable = len([i for i in injuries 
                           if i.get('player', {}).get('type') == 'Questionable'])
        
        # Sakatlık sebeplerini grupla
        reasons = {}
        for injury in injuries:
            reason = injury.get('player', {}).get('reason', 'Unknown')
            reasons[reason] = reasons.get(reason, 0) + 1
        
        return {
            'total_injuries': total_injuries,
            'missing_fixtures': missing_fixtures,
            'questionable': questionable,
            'injury_reasons': reasons,
            'most_common_reason': max(reasons.items(), key=lambda x: x[1])[0] if reasons else None
        }


if __name__ == "__main__":
    # Test injuries service
    print("Testing Injuries Service...")
    
    try:
        with InjuriesService() as service:
            # Test get fixture injuries
            injuries = service.get_fixture_injuries(686314)
            print(f"✓ Fixture injuries: {len(injuries)}")
            
            # Test get missing players
            missing = service.get_missing_players(686314)
            print(f"✓ Missing players: {len(missing)}")
            
            # Test get suspended players
            suspended = service.get_suspended_players(686314)
            print(f"✓ Suspended players: {len(suspended)}")
            
            # Test get team injuries
            team_injuries = service.get_team_injuries(157, 2021)
            print(f"✓ Bayern Munich injuries: {len(team_injuries)}")
            
            # Test get injury statistics
            stats = service.get_team_injury_statistics(157, 2021)
            print(f"✓ Injury statistics - Total: {stats['total_injuries']}")
            
    except Exception as e:
        print(f"✗ Error testing injuries service: {e}")
