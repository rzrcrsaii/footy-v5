"""
API Football Fixture Player Statistics Service Module

Bu modül API Football Fixture Player Statistics endpoint'i için servis sınıfını içerir.
Maçtaki oyuncu istatistiklerini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class FixturePlayerStatisticsService(BaseService):
    """
    API Football Fixture Player Statistics servisi.
    
    Bu servis maçtaki oyuncu istatistiklerini almak için kullanılır.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        FixturePlayerStatisticsService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/fixtures/players'

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

    
    def get_fixture_player_statistics(self, fixture_id: int,
                                     team: Optional[int] = None,
                                     timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Maçtaki oyuncu istatistiklerini alır.
        
        Args:
            fixture_id (int): Maç ID'si (zorunlu)
            team (Optional[int]): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> player_stats_service = FixturePlayerStatisticsService()
            >>> result = player_stats_service.get_fixture_player_statistics(169080)
            >>> print(f"Player statistics found: {result['results']}")
        """
        params = {'fixture': fixture_id}
        
        if team is not None:
            params['team'] = team
        
        return self.get(
            endpoint=self.endpoint,
            params=params,
            timeout=timeout
        )
    
    def get_all_player_stats(self, fixture_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Maçın tüm oyuncu istatistiklerini alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Takım bazlı oyuncu istatistikleri
            
        Usage:
            >>> player_stats_service = FixturePlayerStatisticsService()
            >>> stats = player_stats_service.get_all_player_stats(169080)
            >>> print(f"Teams with player stats: {len(stats)}")
        """
        result = self.get_fixture_player_statistics(fixture_id, timeout=timeout)
        return result.get('response', [])
    
    def get_team_player_stats(self, fixture_id: int, team_id: int,
                             timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir takımın oyuncu istatistiklerini alır.
        
        Args:
            fixture_id (int): Maç ID'si
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Takım oyuncu istatistikleri, bulunamazsa None
            
        Usage:
            >>> player_stats_service = FixturePlayerStatisticsService()
            >>> team_stats = player_stats_service.get_team_player_stats(169080, 2284)
            >>> if team_stats:
            ...     print(f"Players: {len(team_stats['players'])}")
        """
        result = self.get_fixture_player_statistics(fixture_id, team=team_id, timeout=timeout)
        teams = result.get('response', [])
        return teams[0] if teams else None
    
    def get_player_stats_by_id(self, fixture_id: int, player_id: int,
                              timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir oyuncunun maçtaki istatistiklerini alır.
        
        Args:
            fixture_id (int): Maç ID'si
            player_id (int): Oyuncu ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Oyuncu istatistikleri, bulunamazsa None
            
        Usage:
            >>> player_stats_service = FixturePlayerStatisticsService()
            >>> player_stats = player_stats_service.get_player_stats_by_id(169080, 35931)
            >>> if player_stats:
            ...     print(f"Player rating: {player_stats['statistics'][0]['games']['rating']}")
        """
        all_stats = self.get_all_player_stats(fixture_id, timeout=timeout)
        
        for team_data in all_stats:
            for player_data in team_data.get('players', []):
                if player_data.get('player', {}).get('id') == player_id:
                    return player_data
        
        return None
    
    def get_top_rated_players(self, fixture_id: int, count: int = 5,
                             timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Maçın en yüksek puanlı oyuncularını alır.
        
        Args:
            fixture_id (int): Maç ID'si
            count (int): Döndürülecek oyuncu sayısı (varsayılan: 5)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: En yüksek puanlı oyuncular
            
        Usage:
            >>> player_stats_service = FixturePlayerStatisticsService()
            >>> top_players = player_stats_service.get_top_rated_players(169080, 3)
            >>> print(f"Top 3 players: {len(top_players)}")
        """
        all_stats = self.get_all_player_stats(fixture_id, timeout=timeout)
        all_players = []
        
        for team_data in all_stats:
            for player_data in team_data.get('players', []):
                stats = player_data.get('statistics', [])
                if stats and stats[0].get('games', {}).get('rating'):
                    try:
                        rating = float(stats[0]['games']['rating'])
                        player_info = {
                            'player': player_data['player'],
                            'team': team_data['team'],
                            'rating': rating,
                            'statistics': stats[0]
                        }
                        all_players.append(player_info)
                    except (ValueError, TypeError):
                        continue
        
        # Rating'e göre sırala ve ilk count kadarını döndür
        sorted_players = sorted(all_players, key=lambda x: x['rating'], reverse=True)
        return sorted_players[:count]
    
    def get_goal_scorers(self, fixture_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Maçta gol atan oyuncuları alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Gol atan oyuncular
            
        Usage:
            >>> player_stats_service = FixturePlayerStatisticsService()
            >>> scorers = player_stats_service.get_goal_scorers(169080)
            >>> print(f"Goal scorers: {len(scorers)}")
        """
        all_stats = self.get_all_player_stats(fixture_id, timeout=timeout)
        scorers = []
        
        for team_data in all_stats:
            for player_data in team_data.get('players', []):
                stats = player_data.get('statistics', [])
                if stats:
                    goals = stats[0].get('goals', {}).get('total')
                    if goals and goals > 0:
                        scorer_info = {
                            'player': player_data['player'],
                            'team': team_data['team'],
                            'goals': goals,
                            'statistics': stats[0]
                        }
                        scorers.append(scorer_info)
        
        return scorers
    
    def get_assist_providers(self, fixture_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Maçta asist yapan oyuncuları alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Asist yapan oyuncular
            
        Usage:
            >>> player_stats_service = FixturePlayerStatisticsService()
            >>> assisters = player_stats_service.get_assist_providers(169080)
            >>> print(f"Assist providers: {len(assisters)}")
        """
        all_stats = self.get_all_player_stats(fixture_id, timeout=timeout)
        assisters = []
        
        for team_data in all_stats:
            for player_data in team_data.get('players', []):
                stats = player_data.get('statistics', [])
                if stats:
                    assists = stats[0].get('goals', {}).get('assists')
                    if assists and assists > 0:
                        assister_info = {
                            'player': player_data['player'],
                            'team': team_data['team'],
                            'assists': assists,
                            'statistics': stats[0]
                        }
                        assisters.append(assister_info)
        
        return assisters
    
    def get_carded_players(self, fixture_id: int, timeout: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Maçta kart gören oyuncuları alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Kart türüne göre gruplandırılmış oyuncular
            
        Usage:
            >>> player_stats_service = FixturePlayerStatisticsService()
            >>> carded = player_stats_service.get_carded_players(169080)
            >>> print(f"Yellow cards: {len(carded['yellow'])}, Red cards: {len(carded['red'])}")
        """
        all_stats = self.get_all_player_stats(fixture_id, timeout=timeout)
        yellow_cards = []
        red_cards = []
        
        for team_data in all_stats:
            for player_data in team_data.get('players', []):
                stats = player_data.get('statistics', [])
                if stats:
                    cards = stats[0].get('cards', {})
                    
                    if cards.get('yellow', 0) > 0:
                        yellow_info = {
                            'player': player_data['player'],
                            'team': team_data['team'],
                            'yellow_cards': cards['yellow'],
                            'statistics': stats[0]
                        }
                        yellow_cards.append(yellow_info)
                    
                    if cards.get('red', 0) > 0:
                        red_info = {
                            'player': player_data['player'],
                            'team': team_data['team'],
                            'red_cards': cards['red'],
                            'statistics': stats[0]
                        }
                        red_cards.append(red_info)
        
        return {
            'yellow': yellow_cards,
            'red': red_cards
        }
    
    def get_substitutes(self, fixture_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Maçta yedek olarak giren oyuncuları alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Yedek oyuncular
            
        Usage:
            >>> player_stats_service = FixturePlayerStatisticsService()
            >>> subs = player_stats_service.get_substitutes(169080)
            >>> print(f"Substitutes: {len(subs)}")
        """
        all_stats = self.get_all_player_stats(fixture_id, timeout=timeout)
        substitutes = []
        
        for team_data in all_stats:
            for player_data in team_data.get('players', []):
                stats = player_data.get('statistics', [])
                if stats:
                    is_substitute = stats[0].get('games', {}).get('substitute', False)
                    if is_substitute:
                        sub_info = {
                            'player': player_data['player'],
                            'team': team_data['team'],
                            'minutes': stats[0].get('games', {}).get('minutes', 0),
                            'statistics': stats[0]
                        }
                        substitutes.append(sub_info)
        
        return substitutes


if __name__ == "__main__":
    # Test fixture player statistics service
    print("Testing Fixture Player Statistics Service...")
    
    try:
        with FixturePlayerStatisticsService() as service:
            # Test get all player stats
            stats = service.get_all_player_stats(169080)
            print(f"✓ Teams with player stats: {len(stats)}")
            
            # Test get top rated players
            top_players = service.get_top_rated_players(169080, 3)
            print(f"✓ Top 3 players: {len(top_players)}")
            
            # Test get goal scorers
            scorers = service.get_goal_scorers(169080)
            print(f"✓ Goal scorers: {len(scorers)}")
            
            # Test get carded players
            carded = service.get_carded_players(169080)
            print(f"✓ Yellow cards: {len(carded['yellow'])}, Red cards: {len(carded['red'])}")
            
            # Test get substitutes
            subs = service.get_substitutes(169080)
            print(f"✓ Substitutes: {len(subs)}")
            
    except Exception as e:
        print(f"✗ Error testing fixture player statistics service: {e}")
