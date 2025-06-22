"""
API Football Team Countries Service Module

Bu modül API Football Team Countries endpoint'i için servis sınıfını içerir.
Takımlar için mevcut ülke listesini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class TeamCountriesService(BaseService):
    """
    API Football Team Countries servisi.
    
    Bu servis takımlar için mevcut ülke listesini almak için kullanılır.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        TeamCountriesService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/teams/countries'

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

    
    def get_team_countries(self, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Takımlar için mevcut ülke listesini alır.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> countries_service = TeamCountriesService()
            >>> result = countries_service.get_team_countries()
            >>> print(f"Countries found: {result['results']}")
        """
        return self._make_request(
            endpoint=self.endpoint,
            timeout=timeout
        )
    
    def get_all_countries(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Tüm ülkeleri liste olarak döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Ülke listesi
            
        Usage:
            >>> countries_service = TeamCountriesService()
            >>> countries = countries_service.get_all_countries()
            >>> print(f"Total countries: {len(countries)}")
        """
        result = self.get_team_countries(timeout=timeout)
        return result.get('response', [])
    
    def get_country_names(self, timeout: Optional[int] = None) -> List[str]:
        """
        Sadece ülke adlarını liste olarak döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[str]: Ülke adları listesi
            
        Usage:
            >>> countries_service = TeamCountriesService()
            >>> names = countries_service.get_country_names()
            >>> print(f"Country names: {names[:5]}")  # İlk 5 ülke
        """
        countries = self.get_all_countries(timeout=timeout)
        return [country.get('name', '') for country in countries if country.get('name')]
    
    def get_country_codes(self, timeout: Optional[int] = None) -> List[str]:
        """
        Sadece ülke kodlarını liste olarak döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[str]: Ülke kodları listesi
            
        Usage:
            >>> countries_service = TeamCountriesService()
            >>> codes = countries_service.get_country_codes()
            >>> print(f"Country codes: {codes[:5]}")  # İlk 5 kod
        """
        countries = self.get_all_countries(timeout=timeout)
        return [country.get('code', '') for country in countries if country.get('code')]
    
    def get_country_by_name(self, country_name: str, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir ülke adına göre ülke bilgilerini alır.
        
        Args:
            country_name (str): Ülke adı
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Ülke bilgileri, bulunamazsa None
            
        Usage:
            >>> countries_service = TeamCountriesService()
            >>> england = countries_service.get_country_by_name("England")
            >>> if england:
            ...     print(f"Code: {england['code']}, Flag: {england['flag']}")
        """
        countries = self.get_all_countries(timeout=timeout)
        
        for country in countries:
            if country.get('name', '').lower() == country_name.lower():
                return country
        
        return None
    
    def get_country_by_code(self, country_code: str, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir ülke koduna göre ülke bilgilerini alır.
        
        Args:
            country_code (str): Ülke kodu
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Ülke bilgileri, bulunamazsa None
            
        Usage:
            >>> countries_service = TeamCountriesService()
            >>> gb = countries_service.get_country_by_code("GB")
            >>> if gb:
            ...     print(f"Name: {gb['name']}, Flag: {gb['flag']}")
        """
        countries = self.get_all_countries(timeout=timeout)
        
        for country in countries:
            if country.get('code', '').upper() == country_code.upper():
                return country
        
        return None
    
    def search_countries(self, search_term: str, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Ülke adında arama yapar.
        
        Args:
            search_term (str): Arama terimi
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Bulunan ülkeler
            
        Usage:
            >>> countries_service = TeamCountriesService()
            >>> results = countries_service.search_countries("United")
            >>> print(f"Countries with 'United': {len(results)}")
        """
        countries = self.get_all_countries(timeout=timeout)
        search_lower = search_term.lower()
        
        return [country for country in countries 
                if search_lower in country.get('name', '').lower()]
    
    def get_countries_with_flags(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Bayrak URL'si olan ülkeleri döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Bayrak URL'si olan ülkeler
            
        Usage:
            >>> countries_service = TeamCountriesService()
            >>> with_flags = countries_service.get_countries_with_flags()
            >>> print(f"Countries with flags: {len(with_flags)}")
        """
        countries = self.get_all_countries(timeout=timeout)
        
        return [country for country in countries 
                if country.get('flag') and country['flag'].strip()]
    
    def get_countries_count(self, timeout: Optional[int] = None) -> int:
        """
        Toplam ülke sayısını döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            int: Toplam ülke sayısı
            
        Usage:
            >>> countries_service = TeamCountriesService()
            >>> count = countries_service.get_countries_count()
            >>> print(f"Total countries: {count}")
        """
        countries = self.get_all_countries(timeout=timeout)
        return len(countries)
    
    def get_countries_alphabetically(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Ülkeleri alfabetik sıraya göre döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Alfabetik sıralı ülke listesi
            
        Usage:
            >>> countries_service = TeamCountriesService()
            >>> sorted_countries = countries_service.get_countries_alphabetically()
            >>> print(f"First country: {sorted_countries[0]['name']}")
        """
        countries = self.get_all_countries(timeout=timeout)
        
        return sorted(countries, key=lambda x: x.get('name', '').lower())
    
    def get_countries_by_continent(self, timeout: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Ülkeleri kıtalara göre gruplar (basit sınıflandırma).
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Kıtalara göre gruplandırılmış ülkeler
            
        Note:
            Bu basit bir sınıflandırmadır, tam doğruluk için coğrafi API kullanın.
            
        Usage:
            >>> countries_service = TeamCountriesService()
            >>> by_continent = countries_service.get_countries_by_continent()
            >>> print(f"European countries: {len(by_continent.get('Europe', []))}")
        """
        countries = self.get_all_countries(timeout=timeout)
        
        # Basit kıta sınıflandırması (örnek)
        european_codes = ['GB', 'FR', 'DE', 'IT', 'ES', 'NL', 'BE', 'PT', 'GR', 'AT', 'CH', 'SE', 'NO', 'DK', 'FI', 'IE', 'PL', 'CZ', 'HU', 'RO', 'BG', 'HR', 'SI', 'SK', 'LT', 'LV', 'EE', 'LU', 'MT', 'CY']
        asian_codes = ['JP', 'KR', 'CN', 'IN', 'TH', 'VN', 'MY', 'SG', 'ID', 'PH', 'BD', 'PK', 'LK', 'MM', 'KH', 'LA', 'BN', 'MV', 'BT', 'NP']
        african_codes = ['NG', 'ZA', 'EG', 'KE', 'GH', 'MA', 'TN', 'DZ', 'LY', 'SD', 'ET', 'UG', 'TZ', 'MZ', 'MG', 'CM', 'CI', 'NE', 'BF', 'ML']
        american_codes = ['US', 'CA', 'MX', 'BR', 'AR', 'CL', 'CO', 'PE', 'VE', 'EC', 'BO', 'PY', 'UY', 'GY', 'SR', 'GF', 'CR', 'PA', 'GT', 'HN']
        oceanian_codes = ['AU', 'NZ', 'FJ', 'PG', 'SB', 'NC', 'PF', 'VU', 'WS', 'TO', 'KI', 'PW', 'NR', 'FM', 'MH', 'TV']
        
        continents = {
            'Europe': [],
            'Asia': [],
            'Africa': [],
            'Americas': [],
            'Oceania': [],
            'Other': []
        }
        
        for country in countries:
            code = country.get('code', '')
            if code in european_codes:
                continents['Europe'].append(country)
            elif code in asian_codes:
                continents['Asia'].append(country)
            elif code in african_codes:
                continents['Africa'].append(country)
            elif code in american_codes:
                continents['Americas'].append(country)
            elif code in oceanian_codes:
                continents['Oceania'].append(country)
            else:
                continents['Other'].append(country)
        
        return continents
    
    def is_country_available(self, country_name: str, timeout: Optional[int] = None) -> bool:
        """
        Belirtilen ülkenin mevcut olup olmadığını kontrol eder.
        
        Args:
            country_name (str): Ülke adı
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            bool: Ülke mevcut ise True, değilse False
            
        Usage:
            >>> countries_service = TeamCountriesService()
            >>> is_available = countries_service.is_country_available("England")
            >>> print(f"England is available: {is_available}")
        """
        country = self.get_country_by_name(country_name, timeout=timeout)
        return country is not None
    
    def get_flag_url(self, country_name: str, timeout: Optional[int] = None) -> Optional[str]:
        """
        Belirtilen ülkenin bayrak URL'ini döndürür.
        
        Args:
            country_name (str): Ülke adı
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[str]: Bayrak URL'i, bulunamazsa None
            
        Usage:
            >>> countries_service = TeamCountriesService()
            >>> flag_url = countries_service.get_flag_url("England")
            >>> print(f"England flag: {flag_url}")
        """
        country = self.get_country_by_name(country_name, timeout=timeout)
        return country.get('flag') if country else None


if __name__ == "__main__":
    # Test team countries service
    print("Testing Team Countries Service...")
    
    try:
        with TeamCountriesService() as service:
            # Test get all countries
            countries = service.get_all_countries()
            print(f"✓ Total countries: {len(countries)}")
            
            # Test get country names
            names = service.get_country_names()
            print(f"✓ Country names: {names[:3]}")  # İlk 3 ülke
            
            # Test get country by name
            england = service.get_country_by_name("England")
            if england:
                print(f"✓ England found - Code: {england['code']}")
            
            # Test search countries
            united_countries = service.search_countries("United")
            print(f"✓ Countries with 'United': {len(united_countries)}")
            
            # Test get countries with flags
            with_flags = service.get_countries_with_flags()
            print(f"✓ Countries with flags: {len(with_flags)}")
            
            # Test get countries by continent
            by_continent = service.get_countries_by_continent()
            print(f"✓ European countries: {len(by_continent.get('Europe', []))}")
            
    except Exception as e:
        print(f"✗ Error testing team countries service: {e}")
