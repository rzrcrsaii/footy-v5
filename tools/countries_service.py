"""
API Football Countries Service Module

Bu modül API Football Countries endpoint'i için servis sınıfını içerir.
Mevcut ülke listesini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class CountriesService(BaseService):
    """
    API Football Countries servisi.
    
    Bu servis mevcut ülke listesini almak için kullanılır.
    Leagues endpoint'inde country parametresi olarak kullanılabilir.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        CountriesService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/countries'

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

    
    def get_countries(self, name: Optional[str] = None, code: Optional[str] = None,
                     search: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Ülke listesini alır.
        
        Args:
            name (Optional[str]): Ülke adı
            code (Optional[str]): Ülke kodu (2-6 karakter, örn: FR, GB-ENG, IT)
            search (Optional[str]): Arama terimi (3 karakter)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API response içeren ülke listesi
            
        Example Response:
            {
                "get": "countries",
                "parameters": {"name": "england"},
                "errors": [],
                "results": 1,
                "paging": {"current": 1, "total": 1},
                "response": [
                    {
                        "name": "England",
                        "code": "GB",
                        "flag": "https://media.api-sports.io/flags/gb.svg"
                    }
                ]
            }
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> countries_service = CountriesService()
            >>> result = countries_service.get_countries(name="england")
            >>> countries = result['response']
        """
        params = {}
        
        if name:
            params['name'] = name
        if code:
            params['code'] = code
        if search:
            if len(search) < 3:
                raise ValueError("Search parameter must be at least 3 characters long")
            params['search'] = search
        
        return self.get(self.endpoint, params=params, timeout=timeout)
    
    def get_all_countries(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Tüm ülkeleri döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Ülke listesi
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> countries_service = CountriesService()
            >>> countries = countries_service.get_all_countries()
            >>> print(f"Total countries: {len(countries)}")
        """
        result = self.get_countries(timeout=timeout)
        return result.get('response', [])
    
    def get_country_by_name(self, name: str, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        İsme göre ülke bilgisi alır.
        
        Args:
            name (str): Ülke adı
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Ülke bilgisi veya None
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> countries_service = CountriesService()
            >>> country = countries_service.get_country_by_name("England")
            >>> if country:
            >>>     print(f"Country code: {country['code']}")
        """
        if not name:
            return None
        
        result = self.get_countries(name=name, timeout=timeout)
        countries = result.get('response', [])
        return countries[0] if countries else None
    
    def get_country_by_code(self, code: str, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Koda göre ülke bilgisi alır.
        
        Args:
            code (str): Ülke kodu (2-6 karakter)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Ülke bilgisi veya None
            
        Raises:
            APIFootballException: API hatası durumunda
            ValueError: Geçersiz kod formatı
            
        Usage:
            >>> countries_service = CountriesService()
            >>> country = countries_service.get_country_by_code("GB")
            >>> if country:
            >>>     print(f"Country name: {country['name']}")
        """
        if not code:
            return None
        
        if len(code) < 2 or len(code) > 6:
            raise ValueError("Country code must be between 2-6 characters")
        
        result = self.get_countries(code=code, timeout=timeout)
        countries = result.get('response', [])
        return countries[0] if countries else None
    
    def search_countries(self, search_term: str, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Ülke listesinde arama yapar.
        
        Args:
            search_term (str): Arama terimi (minimum 3 karakter)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Arama sonucu ülke listesi
            
        Raises:
            APIFootballException: API hatası durumunda
            ValueError: Geçersiz arama terimi
            
        Usage:
            >>> countries_service = CountriesService()
            >>> countries = countries_service.search_countries("eng")
            >>> print(f"Found countries: {len(countries)}")
        """
        if not search_term:
            return []
        
        if len(search_term) < 3:
            raise ValueError("Search term must be at least 3 characters long")
        
        result = self.get_countries(search=search_term, timeout=timeout)
        return result.get('response', [])
    
    def get_country_flag_url(self, country_code: str) -> str:
        """
        Ülke bayrağı URL'ini oluşturur.
        
        Args:
            country_code (str): Ülke kodu
            
        Returns:
            str: Bayrak URL'i
            
        Usage:
            >>> countries_service = CountriesService()
            >>> flag_url = countries_service.get_country_flag_url("GB")
            >>> print(f"Flag URL: {flag_url}")
        """
        if not country_code:
            return ""
        
        return f"https://media.api-sports.io/flags/{country_code.lower()}.svg"
    
    def is_country_available(self, country_name: str, timeout: Optional[int] = None) -> bool:
        """
        Ülkenin API'de mevcut olup olmadığını kontrol eder.
        
        Args:
            country_name (str): Ülke adı
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            bool: Ülke mevcut ise True
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> countries_service = CountriesService()
            >>> is_available = countries_service.is_country_available("England")
            >>> print(f"England is available: {is_available}")
        """
        if not country_name:
            return False
        
        try:
            country = self.get_country_by_name(country_name, timeout=timeout)
            return country is not None
        except Exception:
            return False
    
    def get_countries_by_continent(self, timeout: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Ülkeleri kıtalara göre gruplar (basit sınıflandırma).
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Kıtalara göre gruplandırılmış ülkeler
            
        Note:
            Bu fonksiyon basit bir sınıflandırma yapar. Tam doğruluk için
            ayrı bir coğrafi veri kaynağı kullanılmalıdır.
            
        Usage:
            >>> countries_service = CountriesService()
            >>> by_continent = countries_service.get_countries_by_continent()
            >>> print(f"European countries: {len(by_continent.get('Europe', []))}")
        """
        countries = self.get_all_countries(timeout=timeout)
        
        # Basit kıta sınıflandırması (tam liste değil)
        continent_mapping = {
            'Europe': ['England', 'France', 'Germany', 'Spain', 'Italy', 'Netherlands', 
                      'Portugal', 'Belgium', 'Switzerland', 'Austria', 'Poland', 'Czech-Republic',
                      'Denmark', 'Sweden', 'Norway', 'Finland', 'Greece', 'Turkey', 'Russia',
                      'Ukraine', 'Croatia', 'Serbia', 'Romania', 'Bulgaria', 'Hungary', 'Slovakia'],
            'South America': ['Brazil', 'Argentina', 'Chile', 'Uruguay', 'Colombia', 'Peru',
                             'Ecuador', 'Bolivia', 'Paraguay', 'Venezuela'],
            'North America': ['USA', 'Mexico', 'Canada', 'Costa-Rica', 'Panama', 'Guatemala',
                             'Honduras', 'El-Salvador', 'Nicaragua'],
            'Asia': ['Japan', 'South-Korea', 'China', 'India', 'Thailand', 'Vietnam',
                    'Malaysia', 'Singapore', 'Indonesia', 'Philippines', 'Iran', 'Iraq',
                    'Saudi-Arabia', 'UAE', 'Qatar', 'Kuwait'],
            'Africa': ['Egypt', 'Morocco', 'Tunisia', 'Algeria', 'Nigeria', 'Ghana',
                      'South-Africa', 'Kenya', 'Cameroon', 'Senegal', 'Ivory-Coast'],
            'Oceania': ['Australia', 'New-Zealand']
        }
        
        result = {continent: [] for continent in continent_mapping.keys()}
        result['Other'] = []
        
        for country in countries:
            country_name = country.get('name', '')
            assigned = False
            
            for continent, country_list in continent_mapping.items():
                if country_name in country_list:
                    result[continent].append(country)
                    assigned = True
                    break
            
            if not assigned:
                result['Other'].append(country)
        
        return result


# Convenience functions
def get_all_countries_list(config: Optional[APIConfig] = None) -> List[Dict[str, Any]]:
    """
    Tüm ülkeleri almak için convenience function.
    
    Args:
        config (Optional[APIConfig]): API konfigürasyonu
        
    Returns:
        List[Dict[str, Any]]: Ülke listesi
    """
    with CountriesService(config) as service:
        return service.get_all_countries()


def find_country(name: str, config: Optional[APIConfig] = None) -> Optional[Dict[str, Any]]:
    """
    Ülke bulmak için convenience function.
    
    Args:
        name (str): Ülke adı
        config (Optional[APIConfig]): API konfigürasyonu
        
    Returns:
        Optional[Dict[str, Any]]: Ülke bilgisi
    """
    with CountriesService(config) as service:
        return service.get_country_by_name(name)


if __name__ == "__main__":
    # Test countries service
    print("Testing Countries Service...")
    
    try:
        with CountriesService() as service:
            # Test get all countries
            countries = service.get_all_countries()
            print(f"✓ Total countries: {len(countries)}")
            
            # Test get country by name
            england = service.get_country_by_name("England")
            if england:
                print(f"✓ England found: {england['name']} ({england['code']})")
            
            # Test search
            search_results = service.search_countries("eng")
            print(f"✓ Search 'eng' found: {len(search_results)} countries")
            
            # Test flag URL
            flag_url = service.get_country_flag_url("GB")
            print(f"✓ Flag URL: {flag_url}")
            
            # Test availability
            is_available = service.is_country_available("England")
            print(f"✓ England is available: {is_available}")
            
    except Exception as e:
        print(f"✗ Countries service test failed: {e}")
