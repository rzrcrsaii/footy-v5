"""
API Football Player Squads Service Module

Bu modül API Football Player Squads endpoint'i için servis sınıfını içerir.
Takım kadroları ve oyuncu takım bilgilerini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class PlayerSquadsService(BaseService):
    """
    API Football Player Squads servisi.
    
    Bu servis takım kadrolarını ve oyuncu takım bilgilerini almak için kullanılır.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        PlayerSquadsService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/players/squads'

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

    
    def get_squads(self, team: Optional[int] = None,
                  player: Optional[int] = None,
                  timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Takım kadrosu veya oyuncu takım bilgilerini alır.
        
        Args:
            team (Optional[int]): Takım ID'si
            player (Optional[int]): Oyuncu ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            ValueError: Hiç parametre verilmezse
            
        Usage:
            >>> squads_service = PlayerSquadsService()
            >>> result = squads_service.get_squads(team=33)
            >>> print(f"Squad data found: {result['results']}")
        """
        params = {}
        
        # En az bir parametre gerekli
        if not any([team, player]):
            raise ValueError("At least one parameter (team or player) is required")
        
        if team is not None:
            params['team'] = team
        
        if player is not None:
            params['player'] = player
        
        return self.get(
            endpoint=self.endpoint,
            params=params,
            timeout=timeout
        )
    
    def get_team_squad(self, team_id: int, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Takımın mevcut kadrosunu alır.
        
        Args:
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Takım kadrosu, bulunamazsa None
            
        Usage:
            >>> squads_service = PlayerSquadsService()
            >>> squad = squads_service.get_team_squad(33)
            >>> if squad:
            ...     print(f"Team: {squad['team']['name']}, Players: {len(squad['players'])}")
        """
        result = self.get_squads(team=team_id, timeout=timeout)
        squads = result.get('response', [])
        return squads[0] if squads else None
    
    def get_player_teams(self, player_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Oyuncunun bağlı olduğu takımları alır.
        
        Args:
            player_id (int): Oyuncu ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Oyuncunun takımları
            
        Usage:
            >>> squads_service = PlayerSquadsService()
            >>> teams = squads_service.get_player_teams(882)
            >>> print(f"Player teams: {len(teams)}")
        """
        result = self.get_squads(player=player_id, timeout=timeout)
        return result.get('response', [])
    
    def get_players_by_position(self, team_id: int, position: str,
                               timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Takımın belirli pozisyondaki oyuncularını alır.
        
        Args:
            team_id (int): Takım ID'si
            position (str): Pozisyon ("Goalkeeper", "Defender", "Midfielder", "Attacker")
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Belirtilen pozisyondaki oyuncular
            
        Usage:
            >>> squads_service = PlayerSquadsService()
            >>> goalkeepers = squads_service.get_players_by_position(33, "Goalkeeper")
            >>> print(f"Goalkeepers: {len(goalkeepers)}")
        """
        squad = self.get_team_squad(team_id, timeout=timeout)
        if not squad:
            return []
        
        return [player for player in squad.get('players', [])
                if player.get('position', '').lower() == position.lower()]
    
    def get_goalkeepers(self, team_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Takımın kalecilerini alır.
        
        Args:
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Kaleciler
            
        Usage:
            >>> squads_service = PlayerSquadsService()
            >>> goalkeepers = squads_service.get_goalkeepers(33)
            >>> print(f"Goalkeepers: {len(goalkeepers)}")
        """
        return self.get_players_by_position(team_id, "Goalkeeper", timeout=timeout)
    
    def get_defenders(self, team_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Takımın defans oyuncularını alır.
        
        Args:
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Defans oyuncuları
            
        Usage:
            >>> squads_service = PlayerSquadsService()
            >>> defenders = squads_service.get_defenders(33)
            >>> print(f"Defenders: {len(defenders)}")
        """
        return self.get_players_by_position(team_id, "Defender", timeout=timeout)
    
    def get_midfielders(self, team_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Takımın orta saha oyuncularını alır.
        
        Args:
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Orta saha oyuncuları
            
        Usage:
            >>> squads_service = PlayerSquadsService()
            >>> midfielders = squads_service.get_midfielders(33)
            >>> print(f"Midfielders: {len(midfielders)}")
        """
        return self.get_players_by_position(team_id, "Midfielder", timeout=timeout)
    
    def get_attackers(self, team_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Takımın forvet oyuncularını alır.
        
        Args:
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Forvet oyuncuları
            
        Usage:
            >>> squads_service = PlayerSquadsService()
            >>> attackers = squads_service.get_attackers(33)
            >>> print(f"Attackers: {len(attackers)}")
        """
        return self.get_players_by_position(team_id, "Attacker", timeout=timeout)
    
    def get_player_by_number(self, team_id: int, number: int,
                            timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Takımda belirli numaralı oyuncuyu bulur.
        
        Args:
            team_id (int): Takım ID'si
            number (int): Forma numarası
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Oyuncu bilgileri, bulunamazsa None
            
        Usage:
            >>> squads_service = PlayerSquadsService()
            >>> player = squads_service.get_player_by_number(33, 10)
            >>> if player:
            ...     print(f"Number 10: {player['name']}")
        """
        squad = self.get_team_squad(team_id, timeout=timeout)
        if not squad:
            return None
        
        for player in squad.get('players', []):
            if player.get('number') == number:
                return player
        
        return None
    
    def get_players_by_age_range(self, team_id: int, min_age: int, max_age: int,
                                timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Takımın belirli yaş aralığındaki oyuncularını alır.
        
        Args:
            team_id (int): Takım ID'si
            min_age (int): Minimum yaş
            max_age (int): Maksimum yaş
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Belirtilen yaş aralığındaki oyuncular
            
        Usage:
            >>> squads_service = PlayerSquadsService()
            >>> young_players = squads_service.get_players_by_age_range(33, 18, 25)
            >>> print(f"Young players (18-25): {len(young_players)}")
        """
        squad = self.get_team_squad(team_id, timeout=timeout)
        if not squad:
            return []
        
        return [player for player in squad.get('players', [])
                if min_age <= player.get('age', 0) <= max_age]
    
    def get_squad_statistics(self, team_id: int, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Takım kadrosu istatistiklerini hesaplar.
        
        Args:
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Kadro istatistikleri, bulunamazsa None
            
        Usage:
            >>> squads_service = PlayerSquadsService()
            >>> stats = squads_service.get_squad_statistics(33)
            >>> if stats:
            ...     print(f"Average age: {stats['average_age']:.1f}")
        """
        squad = self.get_team_squad(team_id, timeout=timeout)
        if not squad:
            return None
        
        players = squad.get('players', [])
        if not players:
            return None
        
        # Pozisyon bazlı sayım
        position_counts = {}
        ages = []
        
        for player in players:
            position = player.get('position', 'Unknown')
            position_counts[position] = position_counts.get(position, 0) + 1
            
            age = player.get('age')
            if age:
                ages.append(age)
        
        # İstatistikleri hesapla
        total_players = len(players)
        average_age = sum(ages) / len(ages) if ages else 0
        youngest_age = min(ages) if ages else 0
        oldest_age = max(ages) if ages else 0
        
        return {
            'total_players': total_players,
            'average_age': average_age,
            'youngest_age': youngest_age,
            'oldest_age': oldest_age,
            'position_counts': position_counts,
            'players_with_numbers': len([p for p in players if p.get('number')])
        }
    
    def search_player_in_squad(self, team_id: int, player_name: str,
                              timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Takım kadrosunda oyuncu adına göre arama yapar.
        
        Args:
            team_id (int): Takım ID'si
            player_name (str): Oyuncu adı (kısmi eşleşme)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Bulunan oyuncular
            
        Usage:
            >>> squads_service = PlayerSquadsService()
            >>> players = squads_service.search_player_in_squad(33, "Rashford")
            >>> print(f"Players found: {len(players)}")
        """
        squad = self.get_team_squad(team_id, timeout=timeout)
        if not squad:
            return []
        
        search_term = player_name.lower()
        return [player for player in squad.get('players', [])
                if search_term in player.get('name', '').lower()]


if __name__ == "__main__":
    # Test player squads service
    print("Testing Player Squads Service...")
    
    try:
        with PlayerSquadsService() as service:
            # Test get team squad
            squad = service.get_team_squad(33)
            if squad:
                print(f"✓ Manchester United squad: {len(squad['players'])} players")
            
            # Test get players by position
            goalkeepers = service.get_goalkeepers(33)
            print(f"✓ Goalkeepers: {len(goalkeepers)}")
            
            defenders = service.get_defenders(33)
            print(f"✓ Defenders: {len(defenders)}")
            
            midfielders = service.get_midfielders(33)
            print(f"✓ Midfielders: {len(midfielders)}")
            
            attackers = service.get_attackers(33)
            print(f"✓ Attackers: {len(attackers)}")
            
            # Test get player by number
            player_10 = service.get_player_by_number(33, 10)
            if player_10:
                print(f"✓ Number 10: {player_10['name']}")
            
            # Test squad statistics
            stats = service.get_squad_statistics(33)
            if stats:
                print(f"✓ Squad stats - Total: {stats['total_players']}, Avg age: {stats['average_age']:.1f}")
            
    except Exception as e:
        print(f"✗ Error testing player squads service: {e}")
