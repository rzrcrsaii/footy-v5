"""
API Football Fixtures Rounds Service Module

Bu modül API Football Fixtures Rounds endpoint'i için servis sınıfını içerir.
Lig turlarını almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class FixturesRoundsService(BaseService):
    """
    API Football Fixtures Rounds servisi.
    
    Bu servis lig turlarını almak için kullanılır.
    Turlar fixtures endpoint'inde filtre olarak kullanılabilir.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        FixturesRoundsService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/fixtures/rounds'

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

    
    def get_rounds(self, league_id: int, season: int,
                  current: Optional[bool] = None,
                  dates: Optional[bool] = None,
                  timezone: Optional[str] = None,
                  timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Lig turlarını alır.
        
        Args:
            league_id (int): Lig ID'si (zorunlu)
            season (int): Sezon (YYYY formatında) (zorunlu)
            current (Optional[bool]): Sadece mevcut tur
            dates (Optional[bool]): Tur tarihlerini dahil et
            timezone (Optional[str]): Zaman dilimi
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> rounds_service = FixturesRoundsService()
            >>> result = rounds_service.get_rounds(39, 2024, dates=True)
            >>> print(f"Rounds found: {result['results']}")
        """
        params = {
            'league': league_id,
            'season': season
        }
        
        if current is not None:
            params['current'] = str(current).lower()
        
        if dates is not None:
            params['dates'] = str(dates).lower()
        
        if timezone is not None:
            params['timezone'] = timezone
        
        return self.get(
            endpoint=self.endpoint,
            params=params,
            timeout=timeout
        )
    
    def get_all_rounds(self, league_id: int, season: int,
                      include_dates: bool = False,
                      timezone: Optional[str] = None,
                      timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Tüm turları alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            include_dates (bool): Tur tarihlerini dahil et (varsayılan: False)
            timezone (Optional[str]): Zaman dilimi
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Tur listesi
            
        Usage:
            >>> rounds_service = FixturesRoundsService()
            >>> rounds = rounds_service.get_all_rounds(39, 2024, include_dates=True)
            >>> print(f"Total rounds: {len(rounds)}")
        """
        result = self.get_rounds(league_id, season, dates=include_dates, 
                               timezone=timezone, timeout=timeout)
        return result.get('response', [])
    
    def get_current_round(self, league_id: int, season: int,
                         include_dates: bool = False,
                         timezone: Optional[str] = None,
                         timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Mevcut turu alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            include_dates (bool): Tur tarihlerini dahil et (varsayılan: False)
            timezone (Optional[str]): Zaman dilimi
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Mevcut tur, bulunamazsa None
            
        Usage:
            >>> rounds_service = FixturesRoundsService()
            >>> current = rounds_service.get_current_round(39, 2024)
            >>> if current:
            ...     print(f"Current round: {current['round']}")
        """
        result = self.get_rounds(league_id, season, current=True, 
                               dates=include_dates, timezone=timezone, timeout=timeout)
        rounds = result.get('response', [])
        return rounds[0] if rounds else None
    
    def get_round_names_only(self, league_id: int, season: int,
                            timeout: Optional[int] = None) -> List[str]:
        """
        Sadece tur adlarını alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[str]: Tur adları listesi
            
        Usage:
            >>> rounds_service = FixturesRoundsService()
            >>> round_names = rounds_service.get_round_names_only(39, 2024)
            >>> print(f"Round names: {round_names[:3]}")  # İlk 3 tur
        """
        rounds = self.get_all_rounds(league_id, season, timeout=timeout)
        
        if isinstance(rounds[0], dict) and 'round' in rounds[0]:
            return [round_data['round'] for round_data in rounds]
        else:
            # Eğer sadece string listesi dönüyorsa
            return rounds
    
    def get_round_by_name(self, league_id: int, season: int, round_name: str,
                         include_dates: bool = False,
                         timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir tur adına göre tur bilgilerini alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            round_name (str): Tur adı
            include_dates (bool): Tur tarihlerini dahil et (varsayılan: False)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Tur bilgileri, bulunamazsa None
            
        Usage:
            >>> rounds_service = FixturesRoundsService()
            >>> round_info = rounds_service.get_round_by_name(39, 2024, "Regular Season - 1")
            >>> if round_info:
            ...     print(f"Round dates: {round_info.get('dates', [])}")
        """
        rounds = self.get_all_rounds(league_id, season, include_dates=include_dates, timeout=timeout)
        
        for round_data in rounds:
            if isinstance(round_data, dict) and round_data.get('round') == round_name:
                return round_data
            elif isinstance(round_data, str) and round_data == round_name:
                return {'round': round_data}
        
        return None
    
    def get_rounds_count(self, league_id: int, season: int,
                        timeout: Optional[int] = None) -> int:
        """
        Toplam tur sayısını döndürür.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            int: Toplam tur sayısı
            
        Usage:
            >>> rounds_service = FixturesRoundsService()
            >>> count = rounds_service.get_rounds_count(39, 2024)
            >>> print(f"Total rounds: {count}")
        """
        rounds = self.get_all_rounds(league_id, season, timeout=timeout)
        return len(rounds)
    
    def get_regular_season_rounds(self, league_id: int, season: int,
                                 include_dates: bool = False,
                                 timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Sadece normal sezon turlarını alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            include_dates (bool): Tur tarihlerini dahil et (varsayılan: False)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Normal sezon turları
            
        Usage:
            >>> rounds_service = FixturesRoundsService()
            >>> regular_rounds = rounds_service.get_regular_season_rounds(39, 2024)
            >>> print(f"Regular season rounds: {len(regular_rounds)}")
        """
        rounds = self.get_all_rounds(league_id, season, include_dates=include_dates, timeout=timeout)
        
        regular_rounds = []
        for round_data in rounds:
            if isinstance(round_data, dict):
                round_name = round_data.get('round', '')
            else:
                round_name = round_data
            
            if 'regular season' in round_name.lower():
                regular_rounds.append(round_data)
        
        return regular_rounds
    
    def get_playoff_rounds(self, league_id: int, season: int,
                          include_dates: bool = False,
                          timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Playoff turlarını alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            include_dates (bool): Tur tarihlerini dahil et (varsayılan: False)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Playoff turları
            
        Usage:
            >>> rounds_service = FixturesRoundsService()
            >>> playoff_rounds = rounds_service.get_playoff_rounds(39, 2024)
            >>> print(f"Playoff rounds: {len(playoff_rounds)}")
        """
        rounds = self.get_all_rounds(league_id, season, include_dates=include_dates, timeout=timeout)
        
        playoff_rounds = []
        for round_data in rounds:
            if isinstance(round_data, dict):
                round_name = round_data.get('round', '')
            else:
                round_name = round_data
            
            if any(keyword in round_name.lower() for keyword in ['playoff', 'final', 'semi', 'quarter']):
                playoff_rounds.append(round_data)
        
        return playoff_rounds
    
    def get_round_dates(self, league_id: int, season: int, round_name: str,
                       timezone: Optional[str] = None,
                       timeout: Optional[int] = None) -> List[str]:
        """
        Belirli bir turun tarihlerini alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            round_name (str): Tur adı
            timezone (Optional[str]): Zaman dilimi
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[str]: Tur tarihleri
            
        Usage:
            >>> rounds_service = FixturesRoundsService()
            >>> dates = rounds_service.get_round_dates(39, 2024, "Regular Season - 1")
            >>> print(f"Round 1 dates: {dates}")
        """
        round_info = self.get_round_by_name(league_id, season, round_name, 
                                          include_dates=True, timeout=timeout)
        return round_info.get('dates', []) if round_info else []
    
    def is_current_round(self, league_id: int, season: int, round_name: str,
                        timeout: Optional[int] = None) -> bool:
        """
        Belirtilen turun mevcut tur olup olmadığını kontrol eder.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            round_name (str): Tur adı
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            bool: Mevcut tur ise True, değilse False
            
        Usage:
            >>> rounds_service = FixturesRoundsService()
            >>> is_current = rounds_service.is_current_round(39, 2024, "Regular Season - 15")
            >>> print(f"Is current round: {is_current}")
        """
        current_round = self.get_current_round(league_id, season, timeout=timeout)
        if current_round:
            current_name = current_round.get('round') if isinstance(current_round, dict) else current_round
            return current_name == round_name
        return False


if __name__ == "__main__":
    # Test fixtures rounds service
    print("Testing Fixtures Rounds Service...")
    
    try:
        with FixturesRoundsService() as service:
            # Test get all rounds
            rounds = service.get_all_rounds(39, 2024, include_dates=True)
            print(f"✓ Total rounds: {len(rounds)}")
            
            # Test get current round
            current = service.get_current_round(39, 2024)
            if current:
                print(f"✓ Current round: {current.get('round', current)}")
            
            # Test get round names only
            round_names = service.get_round_names_only(39, 2024)
            print(f"✓ Round names: {round_names[:3]}")  # İlk 3 tur
            
            # Test get regular season rounds
            regular_rounds = service.get_regular_season_rounds(39, 2024)
            print(f"✓ Regular season rounds: {len(regular_rounds)}")
            
            # Test get round dates
            if rounds:
                first_round_name = rounds[0].get('round') if isinstance(rounds[0], dict) else rounds[0]
                dates = service.get_round_dates(39, 2024, first_round_name)
                print(f"✓ First round dates: {dates}")
            
    except Exception as e:
        print(f"✗ Error testing fixtures rounds service: {e}")
