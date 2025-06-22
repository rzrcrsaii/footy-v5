"""
API Football Fixture Statistics Service Module

Bu modül API Football Fixture Statistics endpoint'i için servis sınıfını içerir.
Maç istatistiklerini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional, Union
from .base_service import BaseService
from .api_config import APIConfig


class FixtureStatisticsService(BaseService):
    """
    API Football Fixture Statistics servisi.
    
    Bu servis maç istatistiklerini almak için kullanılır.
    Şut, pas, faul, top hakimiyeti gibi detaylı maç istatistikleri sağlar.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        FixtureStatisticsService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/fixtures/statistics'

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

    
    def get_fixture_statistics(self, fixture_id: int,
                              team: Optional[int] = None,
                              stat_type: Optional[str] = None,
                              half: Optional[bool] = None,
                              timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Maç istatistiklerini alır.
        
        Args:
            fixture_id (int): Maç ID'si (zorunlu)
            team (Optional[int]): Takım ID'si
            stat_type (Optional[str]): İstatistik türü
            half (Optional[bool]): Yarı istatistikleri dahil et (2024+ sezonlar)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> stats_service = FixtureStatisticsService()
            >>> result = stats_service.get_fixture_statistics(215662)
            >>> print(f"Statistics found: {result['results']}")
        """
        params = {'fixture': fixture_id}
        
        if team is not None:
            params['team'] = team
        
        if stat_type is not None:
            params['type'] = stat_type
        
        if half is not None:
            params['half'] = str(half).lower()
        
        return self.get(
            endpoint=self.endpoint,
            params=params,
            timeout=timeout
        )
    
    def get_all_statistics(self, fixture_id: int, include_half: bool = False,
                          timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Maçın tüm takım istatistiklerini alır.
        
        Args:
            fixture_id (int): Maç ID'si
            include_half (bool): Yarı istatistikleri dahil et (varsayılan: False)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Takım istatistikleri listesi
            
        Usage:
            >>> stats_service = FixtureStatisticsService()
            >>> stats = stats_service.get_all_statistics(215662)
            >>> print(f"Teams with statistics: {len(stats)}")
        """
        result = self.get_fixture_statistics(fixture_id, half=include_half, timeout=timeout)
        return result.get('response', [])
    
    def get_team_statistics(self, fixture_id: int, team_id: int,
                           include_half: bool = False,
                           timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir takımın maç istatistiklerini alır.
        
        Args:
            fixture_id (int): Maç ID'si
            team_id (int): Takım ID'si
            include_half (bool): Yarı istatistikleri dahil et (varsayılan: False)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Takım istatistikleri, bulunamazsa None
            
        Usage:
            >>> stats_service = FixtureStatisticsService()
            >>> team_stats = stats_service.get_team_statistics(215662, 463)
            >>> if team_stats:
            ...     print(f"Team: {team_stats['team']['name']}")
        """
        result = self.get_fixture_statistics(fixture_id, team=team_id, 
                                           half=include_half, timeout=timeout)
        teams = result.get('response', [])
        return teams[0] if teams else None
    
    def get_statistic_value(self, fixture_id: int, team_id: int, stat_type: str,
                           timeout: Optional[int] = None) -> Optional[Union[int, str]]:
        """
        Belirli bir istatistik değerini alır.
        
        Args:
            fixture_id (int): Maç ID'si
            team_id (int): Takım ID'si
            stat_type (str): İstatistik türü (örn: "Shots on Goal", "Ball Possession")
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Union[int, str]]: İstatistik değeri, bulunamazsa None
            
        Usage:
            >>> stats_service = FixtureStatisticsService()
            >>> shots = stats_service.get_statistic_value(215662, 463, "Shots on Goal")
            >>> print(f"Shots on goal: {shots}")
        """
        team_stats = self.get_team_statistics(fixture_id, team_id, timeout=timeout)
        if not team_stats:
            return None
        
        for stat in team_stats.get('statistics', []):
            if stat.get('type') == stat_type:
                return stat.get('value')
        
        return None
    
    def get_possession_stats(self, fixture_id: int, timeout: Optional[int] = None) -> Dict[str, str]:
        """
        Her iki takımın top hakimiyeti istatistiklerini alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, str]: Takım ID'si ve top hakimiyeti yüzdesi
            
        Usage:
            >>> stats_service = FixtureStatisticsService()
            >>> possession = stats_service.get_possession_stats(215662)
            >>> print(f"Possession stats: {possession}")
        """
        all_stats = self.get_all_statistics(fixture_id, timeout=timeout)
        possession_stats = {}
        
        for team_data in all_stats:
            team_id = str(team_data.get('team', {}).get('id', ''))
            team_name = team_data.get('team', {}).get('name', '')
            
            for stat in team_data.get('statistics', []):
                if stat.get('type') == 'Ball Possession':
                    possession_stats[f"{team_name} ({team_id})"] = stat.get('value', '0%')
        
        return possession_stats
    
    def get_shots_comparison(self, fixture_id: int, timeout: Optional[int] = None) -> Dict[str, Dict[str, int]]:
        """
        Her iki takımın şut istatistiklerini karşılaştırır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Dict[str, int]]: Takım bazlı şut istatistikleri
            
        Usage:
            >>> stats_service = FixtureStatisticsService()
            >>> shots = stats_service.get_shots_comparison(215662)
            >>> print(f"Shots comparison: {shots}")
        """
        all_stats = self.get_all_statistics(fixture_id, timeout=timeout)
        shots_stats = {}
        
        for team_data in all_stats:
            team_name = team_data.get('team', {}).get('name', '')
            team_shots = {
                'shots_on_goal': 0,
                'shots_off_goal': 0,
                'total_shots': 0,
                'blocked_shots': 0,
                'shots_inside_box': 0,
                'shots_outside_box': 0
            }
            
            for stat in team_data.get('statistics', []):
                stat_type = stat.get('type', '')
                value = stat.get('value') or 0
                
                if stat_type == 'Shots on Goal':
                    team_shots['shots_on_goal'] = int(value) if isinstance(value, (int, str)) and str(value).isdigit() else 0
                elif stat_type == 'Shots off Goal':
                    team_shots['shots_off_goal'] = int(value) if isinstance(value, (int, str)) and str(value).isdigit() else 0
                elif stat_type == 'Total Shots':
                    team_shots['total_shots'] = int(value) if isinstance(value, (int, str)) and str(value).isdigit() else 0
                elif stat_type == 'Blocked Shots':
                    team_shots['blocked_shots'] = int(value) if isinstance(value, (int, str)) and str(value).isdigit() else 0
                elif stat_type == 'Shots insidebox':
                    team_shots['shots_inside_box'] = int(value) if isinstance(value, (int, str)) and str(value).isdigit() else 0
                elif stat_type == 'Shots outsidebox':
                    team_shots['shots_outside_box'] = int(value) if isinstance(value, (int, str)) and str(value).isdigit() else 0
            
            shots_stats[team_name] = team_shots
        
        return shots_stats
    
    def get_cards_comparison(self, fixture_id: int, timeout: Optional[int] = None) -> Dict[str, Dict[str, int]]:
        """
        Her iki takımın kart istatistiklerini karşılaştırır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Dict[str, int]]: Takım bazlı kart istatistikleri
            
        Usage:
            >>> stats_service = FixtureStatisticsService()
            >>> cards = stats_service.get_cards_comparison(215662)
            >>> print(f"Cards comparison: {cards}")
        """
        all_stats = self.get_all_statistics(fixture_id, timeout=timeout)
        cards_stats = {}
        
        for team_data in all_stats:
            team_name = team_data.get('team', {}).get('name', '')
            team_cards = {'yellow_cards': 0, 'red_cards': 0}
            
            for stat in team_data.get('statistics', []):
                stat_type = stat.get('type', '')
                value = stat.get('value') or 0
                
                if stat_type == 'Yellow Cards':
                    team_cards['yellow_cards'] = int(value) if isinstance(value, (int, str)) and str(value).isdigit() else 0
                elif stat_type == 'Red Cards':
                    team_cards['red_cards'] = int(value) if isinstance(value, (int, str)) and str(value).isdigit() else 0
            
            cards_stats[team_name] = team_cards
        
        return cards_stats
    
    def get_passes_comparison(self, fixture_id: int, timeout: Optional[int] = None) -> Dict[str, Dict[str, Union[int, float]]]:
        """
        Her iki takımın pas istatistiklerini karşılaştırır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Dict[str, Union[int, float]]]: Takım bazlı pas istatistikleri
            
        Usage:
            >>> stats_service = FixtureStatisticsService()
            >>> passes = stats_service.get_passes_comparison(215662)
            >>> print(f"Passes comparison: {passes}")
        """
        all_stats = self.get_all_statistics(fixture_id, timeout=timeout)
        passes_stats = {}
        
        for team_data in all_stats:
            team_name = team_data.get('team', {}).get('name', '')
            team_passes = {
                'total_passes': 0,
                'accurate_passes': 0,
                'pass_accuracy': 0.0
            }
            
            for stat in team_data.get('statistics', []):
                stat_type = stat.get('type', '')
                value = stat.get('value')
                
                if stat_type == 'Total passes' and value:
                    team_passes['total_passes'] = int(value) if isinstance(value, (int, str)) and str(value).isdigit() else 0
                elif stat_type == 'Passes accurate' and value:
                    team_passes['accurate_passes'] = int(value) if isinstance(value, (int, str)) and str(value).isdigit() else 0
            
            # Pas başarı yüzdesini hesapla
            if team_passes['total_passes'] > 0:
                team_passes['pass_accuracy'] = round(
                    (team_passes['accurate_passes'] / team_passes['total_passes']) * 100, 1
                )
            
            passes_stats[team_name] = team_passes
        
        return passes_stats
    
    def get_available_statistics_types(self, fixture_id: int, timeout: Optional[int] = None) -> List[str]:
        """
        Maç için mevcut istatistik türlerini listeler.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[str]: Mevcut istatistik türleri
            
        Usage:
            >>> stats_service = FixtureStatisticsService()
            >>> types = stats_service.get_available_statistics_types(215662)
            >>> print(f"Available statistics: {types}")
        """
        all_stats = self.get_all_statistics(fixture_id, timeout=timeout)
        stat_types = set()
        
        for team_data in all_stats:
            for stat in team_data.get('statistics', []):
                stat_types.add(stat.get('type', ''))
        
        return sorted(list(stat_types))


if __name__ == "__main__":
    # Test fixture statistics service
    print("Testing Fixture Statistics Service...")
    
    try:
        with FixtureStatisticsService() as service:
            # Test get all statistics
            stats = service.get_all_statistics(215662)
            print(f"✓ Teams with statistics: {len(stats)}")
            
            # Test get possession stats
            possession = service.get_possession_stats(215662)
            print(f"✓ Possession stats: {possession}")
            
            # Test get shots comparison
            shots = service.get_shots_comparison(215662)
            print(f"✓ Shots comparison: {len(shots)} teams")
            
            # Test get cards comparison
            cards = service.get_cards_comparison(215662)
            print(f"✓ Cards comparison: {len(cards)} teams")
            
            # Test get passes comparison
            passes = service.get_passes_comparison(215662)
            print(f"✓ Passes comparison: {len(passes)} teams")
            
            # Test get available statistics types
            types = service.get_available_statistics_types(215662)
            print(f"✓ Available statistics types: {len(types)}")
            
    except Exception as e:
        print(f"✗ Error testing fixture statistics service: {e}")
