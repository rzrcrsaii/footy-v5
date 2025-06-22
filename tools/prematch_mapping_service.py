"""
API Football Prematch Mapping Service Module

Bu modül API Football Prematch Mapping endpoint'i için servis sınıfını içerir.
Bahis eşleştirme verilerini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class PrematchMappingService(BaseService):
    """
    API Football Prematch Mapping servisi.
    
    Bu servis bahis eşleştirme verilerini almak için kullanılır.
    Fixture ID'leri ile bahisçi ID'leri arasında eşleştirme sağlar.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        PrematchMappingService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/odds/mapping'

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

    
    def get_mapping(self, fixture: Optional[int] = None,
                   bookmaker: Optional[int] = None,
                   page: int = 1,
                   timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Bahis eşleştirme verilerini alır.
        
        Args:
            fixture (Optional[int]): Maç ID'si
            bookmaker (Optional[int]): Bahisçi ID'si
            page (int): Sayfa numarası (varsayılan: 1)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> mapping_service = PrematchMappingService()
            >>> result = mapping_service.get_mapping(fixture=198772)
            >>> print(f"Mapping data found: {result['results']}")
        """
        params = {'page': page}
        
        if fixture is not None:
            params['fixture'] = fixture
        
        if bookmaker is not None:
            params['bookmaker'] = bookmaker
        
        return self.get(
            endpoint=self.endpoint,
            params=params,
            timeout=timeout
        )
    
    def get_fixture_mapping(self, fixture_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir maçın eşleştirme verilerini alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Maç eşleştirme verileri
            
        Usage:
            >>> mapping_service = PrematchMappingService()
            >>> mapping = mapping_service.get_fixture_mapping(198772)
            >>> print(f"Bookmaker mappings: {len(mapping)}")
        """
        result = self.get_mapping(fixture=fixture_id, timeout=timeout)
        return result.get('response', [])
    
    def get_bookmaker_mapping(self, bookmaker_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir bahisçinin eşleştirme verilerini alır.
        
        Args:
            bookmaker_id (int): Bahisçi ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Bahisçi eşleştirme verileri
            
        Usage:
            >>> mapping_service = PrematchMappingService()
            >>> mapping = mapping_service.get_bookmaker_mapping(6)
            >>> print(f"Bet365 mappings: {len(mapping)}")
        """
        all_mappings = []
        page = 1
        
        while True:
            result = self.get_mapping(bookmaker=bookmaker_id, page=page, timeout=timeout)
            mappings = result.get('response', [])
            
            if not mappings:
                break
            
            all_mappings.extend(mappings)
            
            # Sayfa bilgisini kontrol et
            paging = result.get('paging', {})
            if page >= paging.get('total', 1):
                break
            
            page += 1
        
        return all_mappings
    
    def get_all_mappings(self, max_pages: int = 10, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Tüm eşleştirme verilerini alır (sayfalama ile).
        
        Args:
            max_pages (int): Maksimum sayfa sayısı (varsayılan: 10)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Tüm eşleştirme verileri
            
        Warning:
            Bu fonksiyon çok fazla API çağrısı yapabilir. Dikkatli kullanın.
            
        Usage:
            >>> mapping_service = PrematchMappingService()
            >>> mappings = mapping_service.get_all_mappings(max_pages=3)
            >>> print(f"Total mappings: {len(mappings)}")
        """
        all_mappings = []
        page = 1
        
        while page <= max_pages:
            result = self.get_mapping(page=page, timeout=timeout)
            mappings = result.get('response', [])
            
            if not mappings:
                break
            
            all_mappings.extend(mappings)
            
            # Sayfa bilgisini kontrol et
            paging = result.get('paging', {})
            if page >= paging.get('total', 1):
                break
            
            page += 1
        
        return all_mappings
    
    def get_fixture_bookmaker_id(self, fixture_id: int, bookmaker_id: int,
                                timeout: Optional[int] = None) -> Optional[str]:
        """
        Belirli bir maç ve bahisçi için bahisçi maç ID'sini alır.
        
        Args:
            fixture_id (int): Maç ID'si
            bookmaker_id (int): Bahisçi ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[str]: Bahisçi maç ID'si, bulunamazsa None
            
        Usage:
            >>> mapping_service = PrematchMappingService()
            >>> bookmaker_fixture_id = mapping_service.get_fixture_bookmaker_id(198772, 6)
            >>> print(f"Bet365 fixture ID: {bookmaker_fixture_id}")
        """
        mappings = self.get_fixture_mapping(fixture_id, timeout=timeout)
        
        for mapping in mappings:
            if mapping.get('bookmaker', {}).get('id') == bookmaker_id:
                return mapping.get('fixture', {}).get('bookmaker_id')
        
        return None
    
    def get_available_bookmakers_for_fixture(self, fixture_id: int,
                                           timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir maç için mevcut bahisçileri listeler.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Mevcut bahisçiler
            
        Usage:
            >>> mapping_service = PrematchMappingService()
            >>> bookmakers = mapping_service.get_available_bookmakers_for_fixture(198772)
            >>> print(f"Available bookmakers: {len(bookmakers)}")
        """
        mappings = self.get_fixture_mapping(fixture_id, timeout=timeout)
        
        bookmakers = []
        for mapping in mappings:
            bookmaker_info = mapping.get('bookmaker', {})
            if bookmaker_info:
                bookmakers.append({
                    'id': bookmaker_info.get('id'),
                    'name': bookmaker_info.get('name'),
                    'fixture_id': mapping.get('fixture', {}).get('bookmaker_id')
                })
        
        return bookmakers
    
    def get_fixtures_for_bookmaker(self, bookmaker_id: int, limit: int = 100,
                                  timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir bahisçi için mevcut maçları listeler.
        
        Args:
            bookmaker_id (int): Bahisçi ID'si
            limit (int): Döndürülecek maç sayısı (varsayılan: 100)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Mevcut maçlar
            
        Usage:
            >>> mapping_service = PrematchMappingService()
            >>> fixtures = mapping_service.get_fixtures_for_bookmaker(6, 50)
            >>> print(f"Bet365 fixtures: {len(fixtures)}")
        """
        mappings = self.get_bookmaker_mapping(bookmaker_id, timeout=timeout)
        
        fixtures = []
        for mapping in mappings[:limit]:
            fixture_info = mapping.get('fixture', {})
            if fixture_info:
                fixtures.append({
                    'id': fixture_info.get('id'),
                    'bookmaker_id': fixture_info.get('bookmaker_id'),
                    'bookmaker_name': mapping.get('bookmaker', {}).get('name')
                })
        
        return fixtures
    
    def is_fixture_available_at_bookmaker(self, fixture_id: int, bookmaker_id: int,
                                        timeout: Optional[int] = None) -> bool:
        """
        Belirli bir maçın belirli bir bahisçide mevcut olup olmadığını kontrol eder.
        
        Args:
            fixture_id (int): Maç ID'si
            bookmaker_id (int): Bahisçi ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            bool: Mevcut ise True, değilse False
            
        Usage:
            >>> mapping_service = PrematchMappingService()
            >>> is_available = mapping_service.is_fixture_available_at_bookmaker(198772, 6)
            >>> print(f"Fixture available at Bet365: {is_available}")
        """
        bookmaker_fixture_id = self.get_fixture_bookmaker_id(fixture_id, bookmaker_id, timeout=timeout)
        return bookmaker_fixture_id is not None
    
    def get_mapping_statistics(self, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Eşleştirme istatistiklerini hesaplar.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: Eşleştirme istatistikleri
            
        Usage:
            >>> mapping_service = PrematchMappingService()
            >>> stats = mapping_service.get_mapping_statistics()
            >>> print(f"Total mappings: {stats['total_mappings']}")
        """
        mappings = self.get_all_mappings(max_pages=5, timeout=timeout)  # Sınırlı sayfa
        
        if not mappings:
            return {
                'total_mappings': 0,
                'unique_fixtures': 0,
                'unique_bookmakers': 0,
                'bookmaker_counts': {}
            }
        
        unique_fixtures = set()
        unique_bookmakers = set()
        bookmaker_counts = {}
        
        for mapping in mappings:
            fixture_id = mapping.get('fixture', {}).get('id')
            bookmaker_id = mapping.get('bookmaker', {}).get('id')
            bookmaker_name = mapping.get('bookmaker', {}).get('name', 'Unknown')
            
            if fixture_id:
                unique_fixtures.add(fixture_id)
            
            if bookmaker_id:
                unique_bookmakers.add(bookmaker_id)
                bookmaker_counts[bookmaker_name] = bookmaker_counts.get(bookmaker_name, 0) + 1
        
        return {
            'total_mappings': len(mappings),
            'unique_fixtures': len(unique_fixtures),
            'unique_bookmakers': len(unique_bookmakers),
            'bookmaker_counts': bookmaker_counts
        }
    
    def get_most_covered_fixtures(self, limit: int = 10, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        En çok bahisçi tarafından kapsanan maçları bulur.
        
        Args:
            limit (int): Döndürülecek maç sayısı (varsayılan: 10)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: En çok kapsanan maçlar
            
        Usage:
            >>> mapping_service = PrematchMappingService()
            >>> most_covered = mapping_service.get_most_covered_fixtures(5)
            >>> print(f"Most covered fixtures: {len(most_covered)}")
        """
        mappings = self.get_all_mappings(max_pages=5, timeout=timeout)  # Sınırlı sayfa
        
        fixture_counts = {}
        for mapping in mappings:
            fixture_id = mapping.get('fixture', {}).get('id')
            if fixture_id:
                if fixture_id not in fixture_counts:
                    fixture_counts[fixture_id] = {
                        'fixture_id': fixture_id,
                        'bookmaker_count': 0,
                        'bookmakers': []
                    }
                
                fixture_counts[fixture_id]['bookmaker_count'] += 1
                bookmaker_name = mapping.get('bookmaker', {}).get('name')
                if bookmaker_name:
                    fixture_counts[fixture_id]['bookmakers'].append(bookmaker_name)
        
        # Bahisçi sayısına göre sırala
        sorted_fixtures = sorted(fixture_counts.values(), 
                               key=lambda x: x['bookmaker_count'], reverse=True)
        
        return sorted_fixtures[:limit]
    
    def get_bookmaker_coverage(self, bookmaker_id: int, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Belirli bir bahisçinin kapsama istatistiklerini alır.
        
        Args:
            bookmaker_id (int): Bahisçi ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: Bahisçi kapsama istatistikleri
            
        Usage:
            >>> mapping_service = PrematchMappingService()
            >>> coverage = mapping_service.get_bookmaker_coverage(6)
            >>> print(f"Bet365 coverage: {coverage['fixture_count']} fixtures")
        """
        mappings = self.get_bookmaker_mapping(bookmaker_id, timeout=timeout)
        
        fixture_count = len(set(mapping.get('fixture', {}).get('id') 
                              for mapping in mappings 
                              if mapping.get('fixture', {}).get('id')))
        
        bookmaker_name = mappings[0].get('bookmaker', {}).get('name', 'Unknown') if mappings else 'Unknown'
        
        return {
            'bookmaker_id': bookmaker_id,
            'bookmaker_name': bookmaker_name,
            'total_mappings': len(mappings),
            'fixture_count': fixture_count
        }


if __name__ == "__main__":
    # Test prematch mapping service
    print("Testing Prematch Mapping Service...")
    
    try:
        with PrematchMappingService() as service:
            # Test get fixture mapping
            mapping = service.get_fixture_mapping(198772)
            print(f"✓ Fixture mappings: {len(mapping)}")
            
            # Test get available bookmakers for fixture
            bookmakers = service.get_available_bookmakers_for_fixture(198772)
            print(f"✓ Available bookmakers: {len(bookmakers)}")
            
            # Test get fixture bookmaker ID
            bookmaker_fixture_id = service.get_fixture_bookmaker_id(198772, 6)
            if bookmaker_fixture_id:
                print(f"✓ Bet365 fixture ID: {bookmaker_fixture_id}")
            
            # Test is fixture available at bookmaker
            is_available = service.is_fixture_available_at_bookmaker(198772, 6)
            print(f"✓ Fixture available at Bet365: {is_available}")
            
            # Test get mapping statistics
            stats = service.get_mapping_statistics()
            print(f"✓ Mapping statistics - Total: {stats['total_mappings']}")
            
            # Test get bookmaker coverage
            coverage = service.get_bookmaker_coverage(6)
            print(f"✓ Bet365 coverage: {coverage['fixture_count']} fixtures")
            
    except Exception as e:
        print(f"✗ Error testing prematch mapping service: {e}")
