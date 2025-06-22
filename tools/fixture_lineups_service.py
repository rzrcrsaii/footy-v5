"""
API Football Fixture Lineups Service Module

Bu modül API Football Fixture Lineups endpoint'i için servis sınıfını içerir.
Maç kadro bilgilerini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class FixtureLineupsService(BaseService):
    """
    API Football Fixture Lineups servisi.
    
    Bu servis maç kadro bilgilerini almak için kullanılır.
    İlk 11, yedekler, antrenör ve diziliş bilgileri dahil.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        FixtureLineupsService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/fixtures/lineups'

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

    
    def get_fixture_lineups(self, fixture_id: int,
                           team: Optional[int] = None,
                           player: Optional[int] = None,
                           lineup_type: Optional[str] = None,
                           timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Maç kadro bilgilerini alır.
        
        Args:
            fixture_id (int): Maç ID'si (zorunlu)
            team (Optional[int]): Takım ID'si
            player (Optional[int]): Oyuncu ID'si
            lineup_type (Optional[str]): Kadro tipi
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> lineups_service = FixtureLineupsService()
            >>> result = lineups_service.get_fixture_lineups(592872)
            >>> print(f"Lineups found: {result['results']}")
        """
        params = {'fixture': fixture_id}
        
        if team is not None:
            params['team'] = team
        
        if player is not None:
            params['player'] = player
        
        if lineup_type is not None:
            params['type'] = lineup_type
        
        return self.get(
            endpoint=self.endpoint,
            params=params,
            timeout=timeout
        )
    
    def get_all_lineups(self, fixture_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Maçın tüm takım kadrolarını alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Takım kadroları listesi
            
        Usage:
            >>> lineups_service = FixtureLineupsService()
            >>> lineups = lineups_service.get_all_lineups(592872)
            >>> print(f"Teams with lineups: {len(lineups)}")
        """
        result = self.get_fixture_lineups(fixture_id, timeout=timeout)
        return result.get('response', [])
    
    def get_team_lineup(self, fixture_id: int, team_id: int,
                       timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir takımın kadrosunu alır.
        
        Args:
            fixture_id (int): Maç ID'si
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Takım kadrosu, bulunamazsa None
            
        Usage:
            >>> lineups_service = FixtureLineupsService()
            >>> lineup = lineups_service.get_team_lineup(592872, 50)
            >>> if lineup:
            ...     print(f"Formation: {lineup['formation']}")
        """
        result = self.get_fixture_lineups(fixture_id, team=team_id, timeout=timeout)
        lineups = result.get('response', [])
        return lineups[0] if lineups else None
    
    def get_starting_eleven(self, fixture_id: int, team_id: int,
                           timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Takımın ilk 11'ini alır.
        
        Args:
            fixture_id (int): Maç ID'si
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: İlk 11 oyuncuları
            
        Usage:
            >>> lineups_service = FixtureLineupsService()
            >>> starting_xi = lineups_service.get_starting_eleven(592872, 50)
            >>> print(f"Starting XI: {len(starting_xi)} players")
        """
        lineup = self.get_team_lineup(fixture_id, team_id, timeout=timeout)
        return lineup.get('startXI', []) if lineup else []
    
    def get_substitutes(self, fixture_id: int, team_id: int,
                       timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Takımın yedek oyuncularını alır.
        
        Args:
            fixture_id (int): Maç ID'si
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Yedek oyuncular
            
        Usage:
            >>> lineups_service = FixtureLineupsService()
            >>> subs = lineups_service.get_substitutes(592872, 50)
            >>> print(f"Substitutes: {len(subs)} players")
        """
        lineup = self.get_team_lineup(fixture_id, team_id, timeout=timeout)
        return lineup.get('substitutes', []) if lineup else []
    
    def get_formation(self, fixture_id: int, team_id: int,
                     timeout: Optional[int] = None) -> Optional[str]:
        """
        Takımın dizilişini alır.
        
        Args:
            fixture_id (int): Maç ID'si
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[str]: Diziliş (örn: "4-3-3"), bulunamazsa None
            
        Usage:
            >>> lineups_service = FixtureLineupsService()
            >>> formation = lineups_service.get_formation(592872, 50)
            >>> print(f"Formation: {formation}")
        """
        lineup = self.get_team_lineup(fixture_id, team_id, timeout=timeout)
        return lineup.get('formation') if lineup else None
    
    def get_coach(self, fixture_id: int, team_id: int,
                 timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Takımın antrenör bilgilerini alır.
        
        Args:
            fixture_id (int): Maç ID'si
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Antrenör bilgileri, bulunamazsa None
            
        Usage:
            >>> lineups_service = FixtureLineupsService()
            >>> coach = lineups_service.get_coach(592872, 50)
            >>> if coach:
            ...     print(f"Coach: {coach['name']}")
        """
        lineup = self.get_team_lineup(fixture_id, team_id, timeout=timeout)
        return lineup.get('coach') if lineup else None
    
    def get_player_position(self, fixture_id: int, team_id: int, player_id: int,
                           timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir oyuncunun pozisyon bilgilerini alır.
        
        Args:
            fixture_id (int): Maç ID'si
            team_id (int): Takım ID'si
            player_id (int): Oyuncu ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Oyuncu pozisyon bilgileri, bulunamazsa None
            
        Usage:
            >>> lineups_service = FixtureLineupsService()
            >>> position = lineups_service.get_player_position(592872, 50, 617)
            >>> if position:
            ...     print(f"Player position: {position['pos']}, Grid: {position['grid']}")
        """
        lineup = self.get_team_lineup(fixture_id, team_id, timeout=timeout)
        if not lineup:
            return None
        
        # İlk 11'de ara
        for player_data in lineup.get('startXI', []):
            if player_data.get('player', {}).get('id') == player_id:
                return player_data.get('player')
        
        # Yedeklerde ara
        for player_data in lineup.get('substitutes', []):
            if player_data.get('player', {}).get('id') == player_id:
                return player_data.get('player')
        
        return None
    
    def get_players_by_position(self, fixture_id: int, team_id: int, position: str,
                               timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli pozisyondaki oyuncuları alır.
        
        Args:
            fixture_id (int): Maç ID'si
            team_id (int): Takım ID'si
            position (str): Pozisyon ("G", "D", "M", "F")
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Belirtilen pozisyondaki oyuncular
            
        Usage:
            >>> lineups_service = FixtureLineupsService()
            >>> defenders = lineups_service.get_players_by_position(592872, 50, "D")
            >>> print(f"Defenders: {len(defenders)}")
        """
        lineup = self.get_team_lineup(fixture_id, team_id, timeout=timeout)
        if not lineup:
            return []
        
        players = []
        
        # İlk 11'den pozisyona göre filtrele
        for player_data in lineup.get('startXI', []):
            if player_data.get('player', {}).get('pos') == position:
                players.append(player_data.get('player'))
        
        # Yedeklerden pozisyona göre filtrele
        for player_data in lineup.get('substitutes', []):
            if player_data.get('player', {}).get('pos') == position:
                players.append(player_data.get('player'))
        
        return players
    
    def get_team_colors(self, fixture_id: int, team_id: int,
                       timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Takımın maçtaki renk bilgilerini alır.
        
        Args:
            fixture_id (int): Maç ID'si
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Renk bilgileri, bulunamazsa None
            
        Usage:
            >>> lineups_service = FixtureLineupsService()
            >>> colors = lineups_service.get_team_colors(592872, 50)
            >>> if colors:
            ...     print(f"Player colors: {colors['player']}")
        """
        lineup = self.get_team_lineup(fixture_id, team_id, timeout=timeout)
        if lineup and 'team' in lineup:
            return lineup['team'].get('colors')
        return None
    
    def is_player_starting(self, fixture_id: int, team_id: int, player_id: int,
                          timeout: Optional[int] = None) -> bool:
        """
        Oyuncunun ilk 11'de olup olmadığını kontrol eder.
        
        Args:
            fixture_id (int): Maç ID'si
            team_id (int): Takım ID'si
            player_id (int): Oyuncu ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            bool: İlk 11'de ise True, değilse False
            
        Usage:
            >>> lineups_service = FixtureLineupsService()
            >>> is_starting = lineups_service.is_player_starting(592872, 50, 617)
            >>> print(f"Player is starting: {is_starting}")
        """
        starting_xi = self.get_starting_eleven(fixture_id, team_id, timeout=timeout)
        
        for player_data in starting_xi:
            if player_data.get('player', {}).get('id') == player_id:
                return True
        
        return False


if __name__ == "__main__":
    # Test fixture lineups service
    print("Testing Fixture Lineups Service...")
    
    try:
        with FixtureLineupsService() as service:
            # Test get all lineups
            lineups = service.get_all_lineups(592872)
            print(f"✓ Teams with lineups: {len(lineups)}")
            
            # Test get team lineup
            lineup = service.get_team_lineup(592872, 50)
            if lineup:
                print(f"✓ Manchester City formation: {lineup.get('formation')}")
            
            # Test get starting eleven
            starting_xi = service.get_starting_eleven(592872, 50)
            print(f"✓ Starting XI: {len(starting_xi)} players")
            
            # Test get substitutes
            subs = service.get_substitutes(592872, 50)
            print(f"✓ Substitutes: {len(subs)} players")
            
            # Test get coach
            coach = service.get_coach(592872, 50)
            if coach:
                print(f"✓ Coach: {coach.get('name')}")
            
            # Test get players by position
            defenders = service.get_players_by_position(592872, 50, "D")
            print(f"✓ Defenders: {len(defenders)}")
            
    except Exception as e:
        print(f"✗ Error testing fixture lineups service: {e}")
