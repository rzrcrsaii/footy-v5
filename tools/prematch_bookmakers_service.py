"""
API Football Prematch Bookmakers Service Module

Bu modül API Football Prematch Bookmakers endpoint'i için servis sınıfını içerir.
Bahisçi listesini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class PrematchBookmakersService(BaseService):
    """
    API Football Prematch Bookmakers servisi.
    
    Bu servis bahisçi listesini almak için kullanılır.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        PrematchBookmakersService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/odds/bookmakers'

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

    
    def get_bookmakers(self, bookmaker_id: Optional[str] = None,
                      search: Optional[str] = None,
                      timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Bahisçi listesini alır.
        
        Args:
            bookmaker_id (Optional[str]): Bahisçi ID'si
            search (Optional[str]): Bahisçi adı (min 3 karakter)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            ValueError: search 3 karakterden kısaysa
            
        Usage:
            >>> bookmakers_service = PrematchBookmakersService()
            >>> result = bookmakers_service.get_bookmakers()
            >>> print(f"Bookmakers found: {result['results']}")
        """
        params = {}
        
        if bookmaker_id is not None:
            params['id'] = bookmaker_id
        
        if search is not None:
            if len(search) < 3:
                raise ValueError("Search term must be at least 3 characters")
            params['search'] = search
        
        return self.get(
            endpoint=self.endpoint,
            params=params,
            timeout=timeout
        )
    
    def get_all_bookmakers(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Tüm bahisçileri alır.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Bahisçi listesi
            
        Usage:
            >>> bookmakers_service = PrematchBookmakersService()
            >>> bookmakers = bookmakers_service.get_all_bookmakers()
            >>> print(f"Total bookmakers: {len(bookmakers)}")
        """
        result = self.get_bookmakers(timeout=timeout)
        return result.get('response', [])
    
    def get_bookmaker_by_id(self, bookmaker_id: str, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir bahisçiyi ID'ye göre alır.
        
        Args:
            bookmaker_id (str): Bahisçi ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Bahisçi bilgileri, bulunamazsa None
            
        Usage:
            >>> bookmakers_service = PrematchBookmakersService()
            >>> bookmaker = bookmakers_service.get_bookmaker_by_id("6")
            >>> if bookmaker:
            ...     print(f"Bookmaker: {bookmaker['name']}")
        """
        result = self.get_bookmakers(bookmaker_id=bookmaker_id, timeout=timeout)
        bookmakers = result.get('response', [])
        return bookmakers[0] if bookmakers else None
    
    def search_bookmakers(self, search_term: str, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Bahisçilerde arama yapar.
        
        Args:
            search_term (str): Arama terimi (min 3 karakter)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Bulunan bahisçiler
            
        Usage:
            >>> bookmakers_service = PrematchBookmakersService()
            >>> bookmakers = bookmakers_service.search_bookmakers("bet")
            >>> print(f"Bookmakers with 'bet': {len(bookmakers)}")
        """
        result = self.get_bookmakers(search=search_term, timeout=timeout)
        return result.get('response', [])
    
    def get_bookmaker_names(self, timeout: Optional[int] = None) -> List[str]:
        """
        Tüm bahisçi adlarını liste olarak döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[str]: Bahisçi adları
            
        Usage:
            >>> bookmakers_service = PrematchBookmakersService()
            >>> names = bookmakers_service.get_bookmaker_names()
            >>> print(f"Bookmaker names: {names[:5]}")  # İlk 5 bahisçi
        """
        bookmakers = self.get_all_bookmakers(timeout=timeout)
        return [bookmaker.get('name', '') for bookmaker in bookmakers if bookmaker.get('name')]
    
    def get_bookmaker_ids(self, timeout: Optional[int] = None) -> List[int]:
        """
        Tüm bahisçi ID'lerini liste olarak döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[int]: Bahisçi ID'leri
            
        Usage:
            >>> bookmakers_service = PrematchBookmakersService()
            >>> ids = bookmakers_service.get_bookmaker_ids()
            >>> print(f"Bookmaker IDs: {ids[:10]}")  # İlk 10 ID
        """
        bookmakers = self.get_all_bookmakers(timeout=timeout)
        return [bookmaker.get('id') for bookmaker in bookmakers if bookmaker.get('id') is not None]
    
    def get_popular_bookmakers(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Popüler bahisçileri filtreler (bilinen büyük bahisçiler).
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Popüler bahisçiler
            
        Usage:
            >>> bookmakers_service = PrematchBookmakersService()
            >>> popular = bookmakers_service.get_popular_bookmakers()
            >>> print(f"Popular bookmakers: {len(popular)}")
        """
        bookmakers = self.get_all_bookmakers(timeout=timeout)
        
        # Popüler bahisçi adları (büyük/küçük harf duyarsız)
        popular_names = [
            'bet365', 'betfair', 'william hill', 'ladbrokes', 'paddy power',
            'betway', 'unibet', 'bwin', '888sport', 'betfred', 'coral',
            'skybet', 'betvictor', 'marathon bet', 'pinnacle', '1xbet',
            'betsson', 'betclic', 'betano', 'pokerstars', 'betfair exchange'
        ]
        
        popular_bookmakers = []
        for bookmaker in bookmakers:
            name = bookmaker.get('name', '').lower()
            if any(popular_name in name for popular_name in popular_names):
                popular_bookmakers.append(bookmaker)
        
        return popular_bookmakers
    
    def get_bookmakers_count(self, timeout: Optional[int] = None) -> int:
        """
        Toplam bahisçi sayısını döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            int: Toplam bahisçi sayısı
            
        Usage:
            >>> bookmakers_service = PrematchBookmakersService()
            >>> count = bookmakers_service.get_bookmakers_count()
            >>> print(f"Total bookmakers: {count}")
        """
        bookmakers = self.get_all_bookmakers(timeout=timeout)
        return len(bookmakers)
    
    def get_bookmaker_name_by_id(self, bookmaker_id: int, timeout: Optional[int] = None) -> Optional[str]:
        """
        Bahisçi ID'sine göre bahisçi adını döndürür.
        
        Args:
            bookmaker_id (int): Bahisçi ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[str]: Bahisçi adı, bulunamazsa None
            
        Usage:
            >>> bookmakers_service = PrematchBookmakersService()
            >>> name = bookmakers_service.get_bookmaker_name_by_id(6)
            >>> print(f"Bookmaker 6: {name}")
        """
        bookmaker = self.get_bookmaker_by_id(str(bookmaker_id), timeout=timeout)
        return bookmaker.get('name') if bookmaker else None
    
    def get_bookmaker_id_by_name(self, bookmaker_name: str, timeout: Optional[int] = None) -> Optional[int]:
        """
        Bahisçi adına göre bahisçi ID'sini döndürür.
        
        Args:
            bookmaker_name (str): Bahisçi adı
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[int]: Bahisçi ID'si, bulunamazsa None
            
        Usage:
            >>> bookmakers_service = PrematchBookmakersService()
            >>> bookmaker_id = bookmakers_service.get_bookmaker_id_by_name("Bet365")
            >>> print(f"Bet365 ID: {bookmaker_id}")
        """
        bookmakers = self.get_all_bookmakers(timeout=timeout)
        
        for bookmaker in bookmakers:
            if bookmaker.get('name', '').lower() == bookmaker_name.lower():
                return bookmaker.get('id')
        
        return None
    
    def is_bookmaker_available(self, bookmaker_name: str, timeout: Optional[int] = None) -> bool:
        """
        Belirtilen bahisçinin mevcut olup olmadığını kontrol eder.
        
        Args:
            bookmaker_name (str): Bahisçi adı
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            bool: Bahisçi mevcut ise True, değilse False
            
        Usage:
            >>> bookmakers_service = PrematchBookmakersService()
            >>> is_available = bookmakers_service.is_bookmaker_available("Bet365")
            >>> print(f"Bet365 is available: {is_available}")
        """
        bookmaker_id = self.get_bookmaker_id_by_name(bookmaker_name, timeout=timeout)
        return bookmaker_id is not None
    
    def get_bookmakers_alphabetically(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Bahisçileri alfabetik sıraya göre döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Alfabetik sıralı bahisçi listesi
            
        Usage:
            >>> bookmakers_service = PrematchBookmakersService()
            >>> sorted_bookmakers = bookmakers_service.get_bookmakers_alphabetically()
            >>> print(f"First bookmaker: {sorted_bookmakers[0]['name']}")
        """
        bookmakers = self.get_all_bookmakers(timeout=timeout)
        
        return sorted(bookmakers, key=lambda x: x.get('name', '').lower())
    
    def get_bookmakers_by_region(self, timeout: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Bahisçileri bölgelere göre gruplar (basit sınıflandırma).
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Bölgelere göre gruplandırılmış bahisçiler
            
        Note:
            Bu basit bir sınıflandırmadır, tam doğruluk için coğrafi API kullanın.
            
        Usage:
            >>> bookmakers_service = PrematchBookmakersService()
            >>> by_region = bookmakers_service.get_bookmakers_by_region()
            >>> print(f"UK bookmakers: {len(by_region.get('UK', []))}")
        """
        bookmakers = self.get_all_bookmakers(timeout=timeout)
        
        # Basit bölge sınıflandırması (örnek)
        uk_bookmakers = ['bet365', 'william hill', 'ladbrokes', 'paddy power', 'coral', 'skybet', 'betfred', 'betvictor']
        european_bookmakers = ['betfair', 'unibet', 'bwin', 'betsson', 'betclic', 'betano']
        international_bookmakers = ['pinnacle', '1xbet', 'marathon bet', '888sport']
        
        regions = {
            'UK': [],
            'Europe': [],
            'International': [],
            'Other': []
        }
        
        for bookmaker in bookmakers:
            name = bookmaker.get('name', '').lower()
            categorized = False
            
            if any(uk_name in name for uk_name in uk_bookmakers):
                regions['UK'].append(bookmaker)
                categorized = True
            elif any(eu_name in name for eu_name in european_bookmakers):
                regions['Europe'].append(bookmaker)
                categorized = True
            elif any(int_name in name for int_name in international_bookmakers):
                regions['International'].append(bookmaker)
                categorized = True
            
            if not categorized:
                regions['Other'].append(bookmaker)
        
        return regions
    
    def find_bookmaker_by_partial_name(self, partial_name: str, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Kısmi ada göre bahisçi arar.
        
        Args:
            partial_name (str): Kısmi bahisçi adı
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Bulunan bahisçiler
            
        Usage:
            >>> bookmakers_service = PrematchBookmakersService()
            >>> results = bookmakers_service.find_bookmaker_by_partial_name("bet")
            >>> print(f"Bookmakers with 'bet': {len(results)}")
        """
        bookmakers = self.get_all_bookmakers(timeout=timeout)
        search_lower = partial_name.lower()
        
        return [bookmaker for bookmaker in bookmakers 
                if search_lower in bookmaker.get('name', '').lower()]


if __name__ == "__main__":
    # Test prematch bookmakers service
    print("Testing Prematch Bookmakers Service...")
    
    try:
        with PrematchBookmakersService() as service:
            # Test get all bookmakers
            bookmakers = service.get_all_bookmakers()
            print(f"✓ Total bookmakers: {len(bookmakers)}")
            
            # Test get bookmaker names
            names = service.get_bookmaker_names()
            print(f"✓ Bookmaker names: {names[:3]}")  # İlk 3 bahisçi
            
            # Test search bookmakers
            bet_bookmakers = service.search_bookmakers("bet")
            print(f"✓ Bookmakers with 'bet': {len(bet_bookmakers)}")
            
            # Test get popular bookmakers
            popular = service.get_popular_bookmakers()
            print(f"✓ Popular bookmakers: {len(popular)}")
            
            # Test get bookmakers by region
            by_region = service.get_bookmakers_by_region()
            print(f"✓ UK bookmakers: {len(by_region.get('UK', []))}")
            
            # Test find by partial name
            partial_results = service.find_bookmaker_by_partial_name("365")
            print(f"✓ Bookmakers with '365': {len(partial_results)}")
            
    except Exception as e:
        print(f"✗ Error testing prematch bookmakers service: {e}")
