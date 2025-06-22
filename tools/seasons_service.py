"""
API Football Seasons Service Module

Bu modül API Football Seasons endpoint'i için servis sınıfını içerir.
Mevcut sezon listesini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class SeasonsService(BaseService):
    """
    API Football Seasons servisi.
    
    Bu servis mevcut sezon listesini almak için kullanılır.
    Tüm sezonlar sadece 4 haneli yıl formatındadır (örn: 2018-2019 sezonu için 2018).
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        SeasonsService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/leagues/seasons'

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

    
    def get_seasons(self, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Mevcut sezon listesini alır.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> seasons_service = SeasonsService()
            >>> result = seasons_service.get_seasons()
            >>> print(f"Available seasons: {result['response']}")
        """
        return self._make_request(
            endpoint=self.endpoint,
            timeout=timeout
        )
    
    def get_all_seasons(self, timeout: Optional[int] = None) -> List[int]:
        """
        Tüm mevcut sezonları liste olarak döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[int]: Sezon listesi
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> seasons_service = SeasonsService()
            >>> seasons = seasons_service.get_all_seasons()
            >>> print(f"Total seasons: {len(seasons)}")
        """
        result = self.get_seasons(timeout=timeout)
        return result.get('response', [])
    
    def get_latest_season(self, timeout: Optional[int] = None) -> Optional[int]:
        """
        En son sezonu döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[int]: En son sezon, yoksa None
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> seasons_service = SeasonsService()
            >>> latest = seasons_service.get_latest_season()
            >>> print(f"Latest season: {latest}")
        """
        seasons = self.get_all_seasons(timeout=timeout)
        return max(seasons) if seasons else None
    
    def get_oldest_season(self, timeout: Optional[int] = None) -> Optional[int]:
        """
        En eski sezonu döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[int]: En eski sezon, yoksa None
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> seasons_service = SeasonsService()
            >>> oldest = seasons_service.get_oldest_season()
            >>> print(f"Oldest season: {oldest}")
        """
        seasons = self.get_all_seasons(timeout=timeout)
        return min(seasons) if seasons else None
    
    def is_season_available(self, season: int, timeout: Optional[int] = None) -> bool:
        """
        Belirtilen sezonun mevcut olup olmadığını kontrol eder.
        
        Args:
            season (int): Kontrol edilecek sezon
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            bool: Sezon mevcut ise True, değilse False
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> seasons_service = SeasonsService()
            >>> is_available = seasons_service.is_season_available(2023)
            >>> print(f"2023 season is available: {is_available}")
        """
        seasons = self.get_all_seasons(timeout=timeout)
        return season in seasons
    
    def get_seasons_range(self, start_year: int, end_year: int, 
                         timeout: Optional[int] = None) -> List[int]:
        """
        Belirtilen yıl aralığındaki sezonları döndürür.
        
        Args:
            start_year (int): Başlangıç yılı (dahil)
            end_year (int): Bitiş yılı (dahil)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[int]: Belirtilen aralıktaki sezonlar
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> seasons_service = SeasonsService()
            >>> recent_seasons = seasons_service.get_seasons_range(2020, 2023)
            >>> print(f"Recent seasons: {recent_seasons}")
        """
        if start_year > end_year:
            return []
        
        all_seasons = self.get_all_seasons(timeout=timeout)
        return [season for season in all_seasons 
                if start_year <= season <= end_year]
    
    def get_seasons_count(self, timeout: Optional[int] = None) -> int:
        """
        Toplam sezon sayısını döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            int: Toplam sezon sayısı
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> seasons_service = SeasonsService()
            >>> count = seasons_service.get_seasons_count()
            >>> print(f"Total seasons available: {count}")
        """
        seasons = self.get_all_seasons(timeout=timeout)
        return len(seasons)
    
    def get_recent_seasons(self, count: int = 5, timeout: Optional[int] = None) -> List[int]:
        """
        En son N sezonu döndürür.
        
        Args:
            count (int): Döndürülecek sezon sayısı (varsayılan: 5)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[int]: En son sezonlar (yeniden eskiye doğru sıralı)
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> seasons_service = SeasonsService()
            >>> recent = seasons_service.get_recent_seasons(3)
            >>> print(f"Last 3 seasons: {recent}")
        """
        seasons = self.get_all_seasons(timeout=timeout)
        if not seasons:
            return []
        
        sorted_seasons = sorted(seasons, reverse=True)
        return sorted_seasons[:count]


if __name__ == "__main__":
    # Test seasons service
    print("Testing Seasons Service...")
    
    try:
        with SeasonsService() as service:
            # Test get all seasons
            seasons = service.get_all_seasons()
            print(f"✓ Total seasons: {len(seasons)}")
            
            # Test latest season
            latest = service.get_latest_season()
            print(f"✓ Latest season: {latest}")
            
            # Test oldest season
            oldest = service.get_oldest_season()
            print(f"✓ Oldest season: {oldest}")
            
            # Test season availability
            is_available = service.is_season_available(2023)
            print(f"✓ 2023 season is available: {is_available}")
            
            # Test recent seasons
            recent = service.get_recent_seasons(3)
            print(f"✓ Recent 3 seasons: {recent}")
            
            # Test seasons range
            range_seasons = service.get_seasons_range(2020, 2023)
            print(f"✓ Seasons 2020-2023: {range_seasons}")
            
    except Exception as e:
        print(f"✗ Error testing seasons service: {e}")
