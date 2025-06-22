"""
API Football Player Statistics Service Module

Bu modül API Football Player Statistics endpoint'i için servis sınıfını içerir.
Oyuncu istatistiklerini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class PlayerStatisticsService(BaseService):
    """
    API Football Player Statistics servisi.
    
    Bu servis oyuncu istatistiklerini almak için kullanılır.
    Sayfalama sistemi kullanır (20 sonuç/sayfa).
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        PlayerStatisticsService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/players'

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

    
    def get_player_statistics(self, player_id: Optional[int] = None,
                             team: Optional[int] = None,
                             league: Optional[int] = None,
                             season: Optional[int] = None,
                             search: Optional[str] = None,
                             page: int = 1,
                             timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Oyuncu istatistiklerini alır.
        
        Args:
            player_id (Optional[int]): Oyuncu ID'si
            team (Optional[int]): Takım ID'si
            league (Optional[int]): Lig ID'si
            season (Optional[int]): Sezon (YYYY formatında)
            search (Optional[str]): Oyuncu adı (min 4 karakter)
            page (int): Sayfa numarası (varsayılan: 1)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            ValueError: search 4 karakterden kısaysa
            
        Usage:
            >>> player_stats_service = PlayerStatisticsService()
            >>> result = player_stats_service.get_player_statistics(player_id=276, season=2019)
            >>> print(f"Player statistics found: {result['results']}")
        """
        params = {'page': page}
        
        if player_id is not None:
            params['id'] = player_id
        
        if team is not None:
            params['team'] = team
        
        if league is not None:
            params['league'] = league
        
        if season is not None:
            params['season'] = season
        
        if search is not None:
            if len(search) < 4:
                raise ValueError("Search term must be at least 4 characters")
            params['search'] = search
        
        return self.get(
            endpoint=self.endpoint,
            params=params,
            timeout=timeout
        )
    
    def get_player_stats_by_id(self, player_id: int, season: int,
                              timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir oyuncunun sezon istatistiklerini alır.
        
        Args:
            player_id (int): Oyuncu ID'si
            season (int): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Oyuncu istatistikleri, bulunamazsa None
            
        Usage:
            >>> player_stats_service = PlayerStatisticsService()
            >>> stats = player_stats_service.get_player_stats_by_id(276, 2019)
            >>> if stats:
            ...     print(f"Player: {stats['player']['name']}")
        """
        result = self.get_player_statistics(player_id=player_id, season=season, timeout=timeout)
        players = result.get('response', [])
        return players[0] if players else None
    
    def get_team_players_stats(self, team_id: int, season: int, league_id: Optional[int] = None,
                              timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Takımın oyuncu istatistiklerini alır.
        
        Args:
            team_id (int): Takım ID'si
            season (int): Sezon (YYYY formatında)
            league_id (Optional[int]): Lig ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Takım oyuncu istatistikleri
            
        Usage:
            >>> player_stats_service = PlayerStatisticsService()
            >>> team_stats = player_stats_service.get_team_players_stats(85, 2019)
            >>> print(f"PSG players: {len(team_stats)}")
        """
        all_players = []
        page = 1
        
        while True:
            result = self.get_player_statistics(team=team_id, season=season, 
                                              league=league_id, page=page, timeout=timeout)
            players = result.get('response', [])
            
            if not players:
                break
            
            all_players.extend(players)
            
            # Sayfa bilgisini kontrol et
            paging = result.get('paging', {})
            if page >= paging.get('total', 1):
                break
            
            page += 1
        
        return all_players
    
    def search_players_stats(self, player_name: str, season: int, league_id: Optional[int] = None,
                            timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Oyuncu adına göre istatistik arar.
        
        Args:
            player_name (str): Oyuncu adı (min 4 karakter)
            season (int): Sezon (YYYY formatında)
            league_id (Optional[int]): Lig ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Bulunan oyuncu istatistikleri
            
        Usage:
            >>> player_stats_service = PlayerStatisticsService()
            >>> players = player_stats_service.search_players_stats("Neymar", 2019)
            >>> print(f"Players found: {len(players)}")
        """
        result = self.get_player_statistics(search=player_name, season=season, 
                                          league=league_id, timeout=timeout)
        return result.get('response', [])
    
    def get_player_goals_stats(self, player_id: int, season: int,
                              timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Oyuncunun gol istatistiklerini alır.
        
        Args:
            player_id (int): Oyuncu ID'si
            season (int): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Gol istatistikleri, bulunamazsa None
            
        Usage:
            >>> player_stats_service = PlayerStatisticsService()
            >>> goals = player_stats_service.get_player_goals_stats(276, 2019)
            >>> if goals:
            ...     print(f"Goals: {goals['total']}, Assists: {goals['assists']}")
        """
        player_stats = self.get_player_stats_by_id(player_id, season, timeout=timeout)
        if player_stats and player_stats.get('statistics'):
            return player_stats['statistics'][0].get('goals')
        return None
    
    def get_player_rating(self, player_id: int, season: int,
                         timeout: Optional[int] = None) -> Optional[float]:
        """
        Oyuncunun sezon puanını alır.
        
        Args:
            player_id (int): Oyuncu ID'si
            season (int): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[float]: Oyuncu puanı, bulunamazsa None
            
        Usage:
            >>> player_stats_service = PlayerStatisticsService()
            >>> rating = player_stats_service.get_player_rating(276, 2019)
            >>> print(f"Player rating: {rating}")
        """
        player_stats = self.get_player_stats_by_id(player_id, season, timeout=timeout)
        if player_stats and player_stats.get('statistics'):
            rating_str = player_stats['statistics'][0].get('games', {}).get('rating')
            try:
                return float(rating_str) if rating_str else None
            except (ValueError, TypeError):
                return None
        return None
    
    def get_top_scorers(self, league_id: int, season: int, limit: int = 10,
                       timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Ligin en golcü oyuncularını alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            limit (int): Döndürülecek oyuncu sayısı (varsayılan: 10)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: En golcü oyuncular
            
        Usage:
            >>> player_stats_service = PlayerStatisticsService()
            >>> top_scorers = player_stats_service.get_top_scorers(61, 2019, 5)
            >>> print(f"Top 5 scorers: {len(top_scorers)}")
        """
        all_players = []
        page = 1
        
        # Birkaç sayfa al (performans için sınırlı)
        while page <= 5:  # Max 5 sayfa (100 oyuncu)
            result = self.get_player_statistics(league=league_id, season=season, 
                                              page=page, timeout=timeout)
            players = result.get('response', [])
            
            if not players:
                break
            
            all_players.extend(players)
            page += 1
        
        # Gol sayısına göre sırala
        scored_players = []
        for player_data in all_players:
            if player_data.get('statistics'):
                goals = player_data['statistics'][0].get('goals', {}).get('total', 0)
                if goals and goals > 0:
                    scored_players.append({
                        'player': player_data['player'],
                        'team': player_data['statistics'][0].get('team'),
                        'goals': goals,
                        'assists': player_data['statistics'][0].get('goals', {}).get('assists', 0),
                        'rating': player_data['statistics'][0].get('games', {}).get('rating')
                    })
        
        # Gol sayısına göre sırala ve limit uygula
        scored_players.sort(key=lambda x: x['goals'], reverse=True)
        return scored_players[:limit]
    
    def get_top_assisters(self, league_id: int, season: int, limit: int = 10,
                         timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Ligin en çok asist yapan oyuncularını alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            limit (int): Döndürülecek oyuncu sayısı (varsayılan: 10)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: En çok asist yapan oyuncular
            
        Usage:
            >>> player_stats_service = PlayerStatisticsService()
            >>> top_assisters = player_stats_service.get_top_assisters(61, 2019, 5)
            >>> print(f"Top 5 assisters: {len(top_assisters)}")
        """
        all_players = []
        page = 1
        
        # Birkaç sayfa al (performans için sınırlı)
        while page <= 5:  # Max 5 sayfa (100 oyuncu)
            result = self.get_player_statistics(league=league_id, season=season, 
                                              page=page, timeout=timeout)
            players = result.get('response', [])
            
            if not players:
                break
            
            all_players.extend(players)
            page += 1
        
        # Asist sayısına göre sırala
        assist_players = []
        for player_data in all_players:
            if player_data.get('statistics'):
                assists = player_data['statistics'][0].get('goals', {}).get('assists', 0)
                if assists and assists > 0:
                    assist_players.append({
                        'player': player_data['player'],
                        'team': player_data['statistics'][0].get('team'),
                        'assists': assists,
                        'goals': player_data['statistics'][0].get('goals', {}).get('total', 0),
                        'rating': player_data['statistics'][0].get('games', {}).get('rating')
                    })
        
        # Asist sayısına göre sırala ve limit uygula
        assist_players.sort(key=lambda x: x['assists'], reverse=True)
        return assist_players[:limit]
    
    def get_player_photo_url(self, player_id: int) -> str:
        """
        Oyuncu fotoğrafı URL'ini oluşturur.
        
        Args:
            player_id (int): Oyuncu ID'si
            
        Returns:
            str: Fotoğraf URL'i
            
        Usage:
            >>> player_stats_service = PlayerStatisticsService()
            >>> photo_url = player_stats_service.get_player_photo_url(276)
            >>> print(f"Photo URL: {photo_url}")
        """
        return f"https://media.api-sports.io/football/players/{player_id}.png"


if __name__ == "__main__":
    # Test player statistics service
    print("Testing Player Statistics Service...")
    
    try:
        with PlayerStatisticsService() as service:
            # Test get player stats by ID
            stats = service.get_player_stats_by_id(276, 2019)
            if stats:
                print(f"✓ Player found: {stats['player']['name']}")
            
            # Test get player rating
            rating = service.get_player_rating(276, 2019)
            if rating:
                print(f"✓ Player rating: {rating}")
            
            # Test get player goals stats
            goals = service.get_player_goals_stats(276, 2019)
            if goals:
                print(f"✓ Goals: {goals.get('total')}, Assists: {goals.get('assists')}")
            
            # Test search players
            players = service.search_players_stats("Neymar", 2019)
            print(f"✓ Players found with name 'Neymar': {len(players)}")
            
            # Test get top scorers
            top_scorers = service.get_top_scorers(61, 2019, 3)
            print(f"✓ Top 3 scorers: {len(top_scorers)}")
            
            # Test get photo URL
            photo_url = service.get_player_photo_url(276)
            print(f"✓ Photo URL: {photo_url}")
            
    except Exception as e:
        print(f"✗ Error testing player statistics service: {e}")
