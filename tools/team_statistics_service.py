"""
API Football Team Statistics Service Module

Bu modül API Football Team Statistics endpoint'i için servis sınıfını içerir.
Takım istatistiklerini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
from .base_service import BaseService
from .api_config import APIConfig


class TeamStatisticsService(BaseService):
    """
    API Football Team Statistics servisi.
    
    Bu servis takım istatistiklerini almak için kullanılır.
    Belirli bir lig ve sezondaki takım performansını analiz eder.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        TeamStatisticsService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/teams/statistics'

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

    
    def get_team_statistics(self, league_id: int, season: int, team_id: int,
                           date: Optional[Union[str, date]] = None,
                           timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Takım istatistiklerini alır.
        
        Args:
            league_id (int): Lig ID'si (zorunlu)
            season (int): Sezon (YYYY formatında) (zorunlu)
            team_id (int): Takım ID'si (zorunlu)
            date (Optional[Union[str, date]]): Limit tarihi (YYYY-MM-DD)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> stats_service = TeamStatisticsService()
            >>> result = stats_service.get_team_statistics(39, 2019, 33)
            >>> print(f"Statistics found: {result['results']}")
        """
        params = {
            'league': league_id,
            'season': season,
            'team': team_id
        }
        
        if date is not None:
            if isinstance(date, datetime):
                params['date'] = date.strftime('%Y-%m-%d')
            elif isinstance(date, str):
                params['date'] = date
        
        return self.get(
            endpoint=self.endpoint,
            params=params,
            timeout=timeout
        )
    
    def get_team_stats(self, league_id: int, season: int, team_id: int,
                      date: Optional[Union[str, date]] = None,
                      timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Takım istatistiklerini döndürür (response kısmı).
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            team_id (int): Takım ID'si
            date (Optional[Union[str, date]]): Limit tarihi
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Takım istatistikleri, bulunamazsa None
            
        Usage:
            >>> stats_service = TeamStatisticsService()
            >>> stats = stats_service.get_team_stats(39, 2019, 33)
            >>> if stats:
            ...     print(f"Form: {stats['form']}")
        """
        result = self.get_team_statistics(league_id, season, team_id, date, timeout)
        return result.get('response')
    
    def get_fixture_statistics(self, league_id: int, season: int, team_id: int,
                              timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Takımın maç istatistiklerini alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Maç istatistikleri, bulunamazsa None
            
        Usage:
            >>> stats_service = TeamStatisticsService()
            >>> fixtures = stats_service.get_fixture_statistics(39, 2019, 33)
            >>> if fixtures:
            ...     print(f"Total played: {fixtures['played']['total']}")
        """
        stats = self.get_team_stats(league_id, season, team_id, timeout=timeout)
        return stats.get('fixtures') if stats else None
    
    def get_goal_statistics(self, league_id: int, season: int, team_id: int,
                           timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Takımın gol istatistiklerini alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Gol istatistikleri, bulunamazsa None
            
        Usage:
            >>> stats_service = TeamStatisticsService()
            >>> goals = stats_service.get_goal_statistics(39, 2019, 33)
            >>> if goals:
            ...     print(f"Goals for: {goals['for']['total']['total']}")
        """
        stats = self.get_team_stats(league_id, season, team_id, timeout=timeout)
        return stats.get('goals') if stats else None
    
    def get_team_form(self, league_id: int, season: int, team_id: int,
                     timeout: Optional[int] = None) -> Optional[str]:
        """
        Takımın form durumunu alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[str]: Form string'i (W=Win, D=Draw, L=Loss), bulunamazsa None
            
        Usage:
            >>> stats_service = TeamStatisticsService()
            >>> form = stats_service.get_team_form(39, 2019, 33)
            >>> print(f"Recent form: {form[-5:]}")  # Son 5 maç
        """
        stats = self.get_team_stats(league_id, season, team_id, timeout=timeout)
        return stats.get('form') if stats else None
    
    def get_biggest_statistics(self, league_id: int, season: int, team_id: int,
                              timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Takımın en büyük istatistiklerini alır (en büyük galibiyet, mağlubiyet vb.).
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: En büyük istatistikler, bulunamazsa None
            
        Usage:
            >>> stats_service = TeamStatisticsService()
            >>> biggest = stats_service.get_biggest_statistics(39, 2019, 33)
            >>> if biggest:
            ...     print(f"Biggest win streak: {biggest['streak']['wins']}")
        """
        stats = self.get_team_stats(league_id, season, team_id, timeout=timeout)
        return stats.get('biggest') if stats else None
    
    def get_clean_sheet_stats(self, league_id: int, season: int, team_id: int,
                             timeout: Optional[int] = None) -> Optional[Dict[str, int]]:
        """
        Takımın temiz çıkma istatistiklerini alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, int]]: Temiz çıkma istatistikleri, bulunamazsa None
            
        Usage:
            >>> stats_service = TeamStatisticsService()
            >>> clean_sheets = stats_service.get_clean_sheet_stats(39, 2019, 33)
            >>> if clean_sheets:
            ...     print(f"Total clean sheets: {clean_sheets['total']}")
        """
        stats = self.get_team_stats(league_id, season, team_id, timeout=timeout)
        return stats.get('clean_sheet') if stats else None
    
    def get_penalty_statistics(self, league_id: int, season: int, team_id: int,
                              timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Takımın penaltı istatistiklerini alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Penaltı istatistikleri, bulunamazsa None
            
        Usage:
            >>> stats_service = TeamStatisticsService()
            >>> penalties = stats_service.get_penalty_statistics(39, 2019, 33)
            >>> if penalties:
            ...     print(f"Penalty success rate: {penalties['scored']['percentage']}")
        """
        stats = self.get_team_stats(league_id, season, team_id, timeout=timeout)
        return stats.get('penalty') if stats else None
    
    def get_lineup_statistics(self, league_id: int, season: int, team_id: int,
                             timeout: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Takımın diziliş istatistiklerini alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[List[Dict[str, Any]]]: Diziliş istatistikleri, bulunamazsa None
            
        Usage:
            >>> stats_service = TeamStatisticsService()
            >>> lineups = stats_service.get_lineup_statistics(39, 2019, 33)
            >>> if lineups:
            ...     print(f"Most used formation: {lineups[0]['formation']}")
        """
        stats = self.get_team_stats(league_id, season, team_id, timeout=timeout)
        return stats.get('lineups') if stats else None
    
    def get_card_statistics(self, league_id: int, season: int, team_id: int,
                           timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Takımın kart istatistiklerini alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Kart istatistikleri, bulunamazsa None
            
        Usage:
            >>> stats_service = TeamStatisticsService()
            >>> cards = stats_service.get_card_statistics(39, 2019, 33)
            >>> if cards:
            ...     print(f"Yellow cards in 76-90 min: {cards['yellow']['76-90']['total']}")
        """
        stats = self.get_team_stats(league_id, season, team_id, timeout=timeout)
        return stats.get('cards') if stats else None
    
    def get_win_percentage(self, league_id: int, season: int, team_id: int,
                          timeout: Optional[int] = None) -> Optional[float]:
        """
        Takımın galibiyet yüzdesini hesaplar.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[float]: Galibiyet yüzdesi, bulunamazsa None
            
        Usage:
            >>> stats_service = TeamStatisticsService()
            >>> win_pct = stats_service.get_win_percentage(39, 2019, 33)
            >>> print(f"Win percentage: {win_pct:.1f}%")
        """
        fixtures = self.get_fixture_statistics(league_id, season, team_id, timeout=timeout)
        if fixtures:
            total_played = fixtures.get('played', {}).get('total', 0)
            total_wins = fixtures.get('wins', {}).get('total', 0)
            
            if total_played > 0:
                return (total_wins / total_played) * 100
        
        return None
    
    def get_goals_per_game(self, league_id: int, season: int, team_id: int,
                          timeout: Optional[int] = None) -> Optional[Dict[str, float]]:
        """
        Takımın maç başına gol ortalamasını hesaplar.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            team_id (int): Takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, float]]: Gol ortalamaları, bulunamazsa None
            
        Usage:
            >>> stats_service = TeamStatisticsService()
            >>> goals_avg = stats_service.get_goals_per_game(39, 2019, 33)
            >>> if goals_avg:
            ...     print(f"Goals scored per game: {goals_avg['scored']}")
        """
        goals = self.get_goal_statistics(league_id, season, team_id, timeout=timeout)
        if goals:
            scored_avg = float(goals.get('for', {}).get('average', {}).get('total', '0'))
            conceded_avg = float(goals.get('against', {}).get('average', {}).get('total', '0'))
            
            return {
                'scored': scored_avg,
                'conceded': conceded_avg,
                'difference': scored_avg - conceded_avg
            }
        
        return None


if __name__ == "__main__":
    # Test team statistics service
    print("Testing Team Statistics Service...")
    
    try:
        with TeamStatisticsService() as service:
            # Test get team statistics
            stats = service.get_team_stats(39, 2019, 33)
            if stats:
                print(f"✓ Manchester United stats found")
            
            # Test get team form
            form = service.get_team_form(39, 2019, 33)
            if form:
                print(f"✓ Team form: {form[-10:]}")  # Son 10 maç
            
            # Test get win percentage
            win_pct = service.get_win_percentage(39, 2019, 33)
            if win_pct:
                print(f"✓ Win percentage: {win_pct:.1f}%")
            
            # Test get goals per game
            goals_avg = service.get_goals_per_game(39, 2019, 33)
            if goals_avg:
                print(f"✓ Goals per game - Scored: {goals_avg['scored']}, Conceded: {goals_avg['conceded']}")
            
            # Test get penalty statistics
            penalties = service.get_penalty_statistics(39, 2019, 33)
            if penalties:
                print(f"✓ Penalty success rate: {penalties.get('scored', {}).get('percentage', 'N/A')}")
            
    except Exception as e:
        print(f"✗ Error testing team statistics service: {e}")
