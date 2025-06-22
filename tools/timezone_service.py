"""
API Football Timezone Service Module

Bu modül API Football Timezone endpoint'i için servis sınıfını içerir.
Mevcut timezone listesini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class TimezoneService(BaseService):
    """
    API Football Timezone servisi.
    
    Bu servis mevcut timezone listesini almak için kullanılır.
    Fixtures endpoint'inde timezone parametresi olarak kullanılabilir.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        TimezoneService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/timezone'

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

    
    def get_timezones(self, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Mevcut timezone listesini alır.
        
        Bu endpoint parametre gerektirmez ve tüm mevcut timezone'ları döndürür.
        Fixtures endpoint'inde timezone parametresi olarak kullanılabilir.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API response içeren timezone listesi
            
        Example Response:
            {
                "get": "timezone",
                "parameters": [],
                "errors": [],
                "results": 425,
                "paging": {
                    "current": 1,
                    "total": 1
                },
                "response": [
                    "Africa/Abidjan",
                    "Africa/Accra",
                    "Africa/Addis_Ababa",
                    "Africa/Algiers",
                    "Africa/Asmara",
                    ...
                ]
            }
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> timezone_service = TimezoneService()
            >>> result = timezone_service.get_timezones()
            >>> timezones = result['response']
            >>> print(f"Available timezones: {len(timezones)}")
        """
        return self.get(self.endpoint, timeout=timeout)
    
    def get_timezone_list(self, timeout: Optional[int] = None) -> List[str]:
        """
        Sadece timezone listesini döndürür (response array'i).
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[str]: Timezone listesi
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> timezone_service = TimezoneService()
            >>> timezones = timezone_service.get_timezone_list()
            >>> print(f"First timezone: {timezones[0]}")
        """
        result = self.get_timezones(timeout=timeout)
        return result.get('response', [])
    
    def is_timezone_valid(self, timezone: str, timeout: Optional[int] = None) -> bool:
        """
        Verilen timezone'ın geçerli olup olmadığını kontrol eder.
        
        Args:
            timezone (str): Kontrol edilecek timezone
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            bool: Timezone geçerli ise True, değilse False
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> timezone_service = TimezoneService()
            >>> is_valid = timezone_service.is_timezone_valid("Europe/London")
            >>> print(f"Europe/London is valid: {is_valid}")
        """
        if not timezone:
            return False
        
        timezones = self.get_timezone_list(timeout=timeout)
        return timezone in timezones
    
    def search_timezones(self, search_term: str, timeout: Optional[int] = None) -> List[str]:
        """
        Timezone listesinde arama yapar.
        
        Args:
            search_term (str): Aranacak terim (case-insensitive)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[str]: Arama terimine uyan timezone listesi
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> timezone_service = TimezoneService()
            >>> europe_timezones = timezone_service.search_timezones("Europe")
            >>> print(f"Europe timezones: {len(europe_timezones)}")
        """
        if not search_term:
            return []
        
        timezones = self.get_timezone_list(timeout=timeout)
        search_term_lower = search_term.lower()
        
        return [tz for tz in timezones if search_term_lower in tz.lower()]
    
    def get_timezone_by_continent(self, continent: str, timeout: Optional[int] = None) -> List[str]:
        """
        Belirli bir kıtaya ait timezone'ları döndürür.
        
        Args:
            continent (str): Kıta adı (örn: "Europe", "America", "Asia", "Africa")
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[str]: Belirtilen kıtaya ait timezone listesi
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> timezone_service = TimezoneService()
            >>> asia_timezones = timezone_service.get_timezone_by_continent("Asia")
            >>> print(f"Asia timezones: {len(asia_timezones)}")
        """
        if not continent:
            return []
        
        timezones = self.get_timezone_list(timeout=timeout)
        continent_prefix = f"{continent}/"
        
        return [tz for tz in timezones if tz.startswith(continent_prefix)]
    
    def get_popular_timezones(self, timeout: Optional[int] = None) -> List[str]:
        """
        Popüler timezone'ları döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[str]: Popüler timezone listesi
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> timezone_service = TimezoneService()
            >>> popular = timezone_service.get_popular_timezones()
            >>> print(f"Popular timezones: {popular}")
        """
        popular_timezones = [
            "UTC",
            "Europe/London",
            "Europe/Paris",
            "Europe/Berlin",
            "Europe/Madrid",
            "Europe/Rome",
            "America/New_York",
            "America/Los_Angeles",
            "America/Chicago",
            "Asia/Tokyo",
            "Asia/Shanghai",
            "Asia/Kolkata",
            "Australia/Sydney",
            "America/Sao_Paulo"
        ]
        
        all_timezones = self.get_timezone_list(timeout=timeout)
        return [tz for tz in popular_timezones if tz in all_timezones]


# Convenience functions
def get_all_timezones(config: Optional[APIConfig] = None) -> List[str]:
    """
    Tüm timezone'ları almak için convenience function.
    
    Args:
        config (Optional[APIConfig]): API konfigürasyonu
        
    Returns:
        List[str]: Timezone listesi
    """
    with TimezoneService(config) as service:
        return service.get_timezone_list()


def validate_timezone(timezone: str, config: Optional[APIConfig] = None) -> bool:
    """
    Timezone doğrulaması için convenience function.
    
    Args:
        timezone (str): Doğrulanacak timezone
        config (Optional[APIConfig]): API konfigürasyonu
        
    Returns:
        bool: Timezone geçerli ise True
    """
    with TimezoneService(config) as service:
        return service.is_timezone_valid(timezone)


if __name__ == "__main__":
    # Test timezone service
    print("Testing Timezone Service...")
    
    try:
        with TimezoneService() as service:
            # Test get all timezones
            result = service.get_timezones()
            print(f"✓ Total timezones: {result.get('results', 0)}")
            
            # Test timezone list
            timezones = service.get_timezone_list()
            print(f"✓ Timezone list length: {len(timezones)}")
            
            # Test timezone validation
            is_valid = service.is_timezone_valid("Europe/London")
            print(f"✓ Europe/London is valid: {is_valid}")
            
            # Test search
            europe_timezones = service.search_timezones("Europe")
            print(f"✓ Europe timezones found: {len(europe_timezones)}")
            
            # Test popular timezones
            popular = service.get_popular_timezones()
            print(f"✓ Popular timezones: {len(popular)}")
            
    except Exception as e:
        print(f"✗ Timezone service test failed: {e}")
