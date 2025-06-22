"""
API Football Standings Service Module

Bu modül API Football Standings endpoint'i için servis sınıfını içerir.
Lig puan durumlarını almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class StandingsService(BaseService):
    """
    API Football Standings servisi.
    
    Bu servis lig puan durumlarını almak için kullanılır.
    Bir lig veya takım için puan durumu tablosu döndürür.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        StandingsService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/standings'

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

    
    def get_standings(self, league: Optional[int] = None, season: int = None,
                     team: Optional[int] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Puan durumunu alır.
        
        Args:
            league (Optional[int]): Lig ID'si
            season (int): Sezon (YYYY formatında) - zorunlu
            team (Optional[int]): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            ValueError: season parametresi verilmezse
            
        Usage:
            >>> standings_service = StandingsService()
            >>> result = standings_service.get_standings(league=39, season=2023)
            >>> print(f"Standings found: {result['results']}")
        """
        if season is None:
            raise ValueError("Season parameter is required")
        
        params = {'season': season}
        
        if league is not None:
            params['league'] = league
        
        if team is not None:
            params['team'] = team
        
        return self.get(
            endpoint=self.endpoint,
            params=params,
            timeout=timeout
        )
    
    def get_league_standings(self, league_id: int, season: int,
                           timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir lig için puan durumunu alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Puan durumu listesi
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> standings_service = StandingsService()
            >>> standings = standings_service.get_league_standings(39, 2023)
            >>> print(f"Premier League standings: {len(standings)} groups")
        """
        result = self.get_standings(league=league_id, season=season, timeout=timeout)
        response = result.get('response', [])
        
        if response:
            return response[0].get('league', {}).get('standings', [])
        return []
    
    def get_team_standing(self, team_id: int, season: int,
                         timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir takımın puan durumunu alır.
        
        Args:
            team_id (int): Takım ID'si
            season (int): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Takım puan durumu, bulunamazsa None
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> standings_service = StandingsService()
            >>> team_standing = standings_service.get_team_standing(33, 2023)
            >>> if team_standing:
            ...     print(f"Manchester United position: {team_standing['rank']}")
        """
        result = self.get_standings(team=team_id, season=season, timeout=timeout)
        response = result.get('response', [])
        
        if response:
            standings = response[0].get('league', {}).get('standings', [])
            for group in standings:
                for team_data in group:
                    if team_data.get('team', {}).get('id') == team_id:
                        return team_data
        return None
    
    def get_top_teams(self, league_id: int, season: int, count: int = 5,
                     timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Ligin en iyi takımlarını alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            count (int): Döndürülecek takım sayısı (varsayılan: 5)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: En iyi takımlar listesi
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> standings_service = StandingsService()
            >>> top_teams = standings_service.get_top_teams(39, 2023, 3)
            >>> print(f"Top 3 teams: {[team['team']['name'] for team in top_teams]}")
        """
        standings = self.get_league_standings(league_id, season, timeout=timeout)
        
        if standings and len(standings) > 0:
            # İlk grup (genellikle ana lig tablosu)
            main_table = standings[0]
            return main_table[:count]
        return []
    
    def get_bottom_teams(self, league_id: int, season: int, count: int = 3,
                        timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Ligin en kötü takımlarını alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            count (int): Döndürülecek takım sayısı (varsayılan: 3)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: En kötü takımlar listesi
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> standings_service = StandingsService()
            >>> bottom_teams = standings_service.get_bottom_teams(39, 2023)
            >>> print(f"Bottom 3 teams: {[team['team']['name'] for team in bottom_teams]}")
        """
        standings = self.get_league_standings(league_id, season, timeout=timeout)
        
        if standings and len(standings) > 0:
            # İlk grup (genellikle ana lig tablosu)
            main_table = standings[0]
            return main_table[-count:] if len(main_table) >= count else main_table
        return []
    
    def get_team_position(self, team_id: int, season: int,
                         timeout: Optional[int] = None) -> Optional[int]:
        """
        Takımın ligdeki sırasını döndürür.
        
        Args:
            team_id (int): Takım ID'si
            season (int): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[int]: Takımın sırası, bulunamazsa None
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> standings_service = StandingsService()
            >>> position = standings_service.get_team_position(33, 2023)
            >>> print(f"Manchester United position: {position}")
        """
        team_standing = self.get_team_standing(team_id, season, timeout=timeout)
        return team_standing.get('rank') if team_standing else None
    
    def get_team_points(self, team_id: int, season: int,
                       timeout: Optional[int] = None) -> Optional[int]:
        """
        Takımın puanını döndürür.
        
        Args:
            team_id (int): Takım ID'si
            season (int): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[int]: Takımın puanı, bulunamazsa None
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> standings_service = StandingsService()
            >>> points = standings_service.get_team_points(33, 2023)
            >>> print(f"Manchester United points: {points}")
        """
        team_standing = self.get_team_standing(team_id, season, timeout=timeout)
        return team_standing.get('points') if team_standing else None
    
    def get_teams_in_european_positions(self, league_id: int, season: int,
                                      timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Avrupa kupalarına katılım hakkı kazanan takımları döndürür.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Avrupa kupalarına katılacak takımlar
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> standings_service = StandingsService()
            >>> european_teams = standings_service.get_teams_in_european_positions(39, 2023)
            >>> print(f"European qualification teams: {len(european_teams)}")
        """
        standings = self.get_league_standings(league_id, season, timeout=timeout)
        
        if standings and len(standings) > 0:
            main_table = standings[0]
            european_teams = []
            
            for team in main_table:
                description = team.get('description', '').lower()
                if any(keyword in description for keyword in 
                      ['champions league', 'europa league', 'conference league', 'promotion']):
                    european_teams.append(team)
            
            return european_teams
        return []


if __name__ == "__main__":
    # Test standings service
    print("Testing Standings Service...")
    
    try:
        with StandingsService() as service:
            # Test get league standings
            standings = service.get_league_standings(39, 2023)
            print(f"✓ Premier League standings groups: {len(standings)}")
            
            # Test get top teams
            top_teams = service.get_top_teams(39, 2023, 3)
            print(f"✓ Top 3 teams: {len(top_teams)}")
            
            # Test get team standing
            team_standing = service.get_team_standing(33, 2023)
            if team_standing:
                print(f"✓ Manchester United position: {team_standing.get('rank')}")
            
            # Test get team position
            position = service.get_team_position(33, 2023)
            print(f"✓ Manchester United position (direct): {position}")
            
            # Test get european teams
            european_teams = service.get_teams_in_european_positions(39, 2023)
            print(f"✓ European qualification teams: {len(european_teams)}")
            
    except Exception as e:
        print(f"✗ Error testing standings service: {e}")
