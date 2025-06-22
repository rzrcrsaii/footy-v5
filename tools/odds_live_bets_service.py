"""
API Football Odds Live Bets Service Module

Bu modül API Football Odds Live Bets endpoint'i için servis sınıfını içerir.
Canlı bahis türlerini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class OddsLiveBetsService(BaseService):
    """
    API Football Odds Live Bets servisi.
    
    Bu servis canlı bahis türlerini almak için kullanılır.
    Tüm mevcut bahis ID'leri odds/live endpoint'inde filtre olarak kullanılabilir.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        OddsLiveBetsService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/odds/live/bets'

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

    
    def get_live_bets(self, bet_id: Optional[str] = None,
                     search: Optional[str] = None,
                     timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Canlı bahis türlerini alır.
        
        Args:
            bet_id (Optional[str]): Bahis ID'si
            search (Optional[str]): Bahis adı (min 3 karakter)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            ValueError: search 3 karakterden kısaysa
            
        Usage:
            >>> bets_service = OddsLiveBetsService()
            >>> result = bets_service.get_live_bets()
            >>> print(f"Live bets found: {result['results']}")
        """
        params = {}
        
        if bet_id is not None:
            params['id'] = bet_id
        
        if search is not None:
            if len(search) < 3:
                raise ValueError("Search term must be at least 3 characters")
            params['search'] = search
        
        return self.get(
            endpoint=self.endpoint,
            params=params,
            timeout=timeout
        )
    
    def get_all_bets(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Tüm canlı bahis türlerini alır.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Bahis türleri listesi
            
        Usage:
            >>> bets_service = OddsLiveBetsService()
            >>> bets = bets_service.get_all_bets()
            >>> print(f"Total live bets: {len(bets)}")
        """
        result = self.get_live_bets(timeout=timeout)
        return result.get('response', [])
    
    def get_bet_by_id(self, bet_id: str, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir bahis türünü ID'ye göre alır.
        
        Args:
            bet_id (str): Bahis ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Bahis türü, bulunamazsa None
            
        Usage:
            >>> bets_service = OddsLiveBetsService()
            >>> bet = bets_service.get_bet_by_id("36")
            >>> if bet:
            ...     print(f"Bet: {bet['name']}")
        """
        result = self.get_live_bets(bet_id=bet_id, timeout=timeout)
        bets = result.get('response', [])
        return bets[0] if bets else None
    
    def search_bets(self, search_term: str, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Bahis türlerinde arama yapar.
        
        Args:
            search_term (str): Arama terimi (min 3 karakter)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Bulunan bahis türleri
            
        Usage:
            >>> bets_service = OddsLiveBetsService()
            >>> bets = bets_service.search_bets("Over")
            >>> print(f"Over/Under bets: {len(bets)}")
        """
        result = self.get_live_bets(search=search_term, timeout=timeout)
        return result.get('response', [])
    
    def get_bet_names(self, timeout: Optional[int] = None) -> List[str]:
        """
        Tüm bahis türü adlarını liste olarak döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[str]: Bahis türü adları
            
        Usage:
            >>> bets_service = OddsLiveBetsService()
            >>> names = bets_service.get_bet_names()
            >>> print(f"Bet names: {names[:5]}")  # İlk 5 bahis türü
        """
        bets = self.get_all_bets(timeout=timeout)
        return [bet.get('name', '') for bet in bets if bet.get('name')]
    
    def get_bet_ids(self, timeout: Optional[int] = None) -> List[int]:
        """
        Tüm bahis ID'lerini liste olarak döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[int]: Bahis ID'leri
            
        Usage:
            >>> bets_service = OddsLiveBetsService()
            >>> ids = bets_service.get_bet_ids()
            >>> print(f"Bet IDs: {ids[:10]}")  # İlk 10 ID
        """
        bets = self.get_all_bets(timeout=timeout)
        return [bet.get('id') for bet in bets if bet.get('id') is not None]
    
    def get_over_under_bets(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Over/Under türü bahisleri filtreler.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Over/Under bahis türleri
            
        Usage:
            >>> bets_service = OddsLiveBetsService()
            >>> ou_bets = bets_service.get_over_under_bets()
            >>> print(f"Over/Under bets: {len(ou_bets)}")
        """
        bets = self.get_all_bets(timeout=timeout)
        return [bet for bet in bets 
                if 'over' in bet.get('name', '').lower() or 'under' in bet.get('name', '').lower()]
    
    def get_asian_handicap_bets(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Asian Handicap türü bahisleri filtreler.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Asian Handicap bahis türleri
            
        Usage:
            >>> bets_service = OddsLiveBetsService()
            >>> ah_bets = bets_service.get_asian_handicap_bets()
            >>> print(f"Asian Handicap bets: {len(ah_bets)}")
        """
        bets = self.get_all_bets(timeout=timeout)
        return [bet for bet in bets 
                if 'asian' in bet.get('name', '').lower() and 'handicap' in bet.get('name', '').lower()]
    
    def get_corner_bets(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Korner türü bahisleri filtreler.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Korner bahis türleri
            
        Usage:
            >>> bets_service = OddsLiveBetsService()
            >>> corner_bets = bets_service.get_corner_bets()
            >>> print(f"Corner bets: {len(corner_bets)}")
        """
        bets = self.get_all_bets(timeout=timeout)
        return [bet for bet in bets 
                if 'corner' in bet.get('name', '').lower()]
    
    def get_goal_scorer_bets(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Gol atan oyuncu türü bahisleri filtreler.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Gol atan oyuncu bahis türleri
            
        Usage:
            >>> bets_service = OddsLiveBetsService()
            >>> scorer_bets = bets_service.get_goal_scorer_bets()
            >>> print(f"Goal scorer bets: {len(scorer_bets)}")
        """
        bets = self.get_all_bets(timeout=timeout)
        return [bet for bet in bets 
                if 'scorer' in bet.get('name', '').lower() or 'score' in bet.get('name', '').lower()]
    
    def get_half_time_bets(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        İlk yarı türü bahisleri filtreler.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: İlk yarı bahis türleri
            
        Usage:
            >>> bets_service = OddsLiveBetsService()
            >>> ht_bets = bets_service.get_half_time_bets()
            >>> print(f"Half time bets: {len(ht_bets)}")
        """
        bets = self.get_all_bets(timeout=timeout)
        return [bet for bet in bets 
                if '1st half' in bet.get('name', '').lower() or 'half time' in bet.get('name', '').lower()]
    
    def get_extra_time_bets(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Uzatma türü bahisleri filtreler.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Uzatma bahis türleri
            
        Usage:
            >>> bets_service = OddsLiveBetsService()
            >>> et_bets = bets_service.get_extra_time_bets()
            >>> print(f"Extra time bets: {len(et_bets)}")
        """
        bets = self.get_all_bets(timeout=timeout)
        return [bet for bet in bets 
                if 'extra time' in bet.get('name', '').lower()]
    
    def get_penalty_bets(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Penaltı türü bahisleri filtreler.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Penaltı bahis türleri
            
        Usage:
            >>> bets_service = OddsLiveBetsService()
            >>> penalty_bets = bets_service.get_penalty_bets()
            >>> print(f"Penalty bets: {len(penalty_bets)}")
        """
        bets = self.get_all_bets(timeout=timeout)
        return [bet for bet in bets 
                if 'penalty' in bet.get('name', '').lower() or 'penalties' in bet.get('name', '').lower()]
    
    def get_bets_count(self, timeout: Optional[int] = None) -> int:
        """
        Toplam bahis türü sayısını döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            int: Toplam bahis türü sayısı
            
        Usage:
            >>> bets_service = OddsLiveBetsService()
            >>> count = bets_service.get_bets_count()
            >>> print(f"Total live bets: {count}")
        """
        bets = self.get_all_bets(timeout=timeout)
        return len(bets)
    
    def get_bet_name_by_id(self, bet_id: int, timeout: Optional[int] = None) -> Optional[str]:
        """
        Bahis ID'sine göre bahis adını döndürür.
        
        Args:
            bet_id (int): Bahis ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[str]: Bahis adı, bulunamazsa None
            
        Usage:
            >>> bets_service = OddsLiveBetsService()
            >>> name = bets_service.get_bet_name_by_id(36)
            >>> print(f"Bet 36: {name}")
        """
        bet = self.get_bet_by_id(str(bet_id), timeout=timeout)
        return bet.get('name') if bet else None
    
    def get_bet_id_by_name(self, bet_name: str, timeout: Optional[int] = None) -> Optional[int]:
        """
        Bahis adına göre bahis ID'sini döndürür.
        
        Args:
            bet_name (str): Bahis adı
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[int]: Bahis ID'si, bulunamazsa None
            
        Usage:
            >>> bets_service = OddsLiveBetsService()
            >>> bet_id = bets_service.get_bet_id_by_name("Over/Under Line")
            >>> print(f"Over/Under Line ID: {bet_id}")
        """
        bets = self.get_all_bets(timeout=timeout)
        
        for bet in bets:
            if bet.get('name', '').lower() == bet_name.lower():
                return bet.get('id')
        
        return None
    
    def get_bets_by_category(self, timeout: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Bahis türlerini kategorilere göre gruplar.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Kategorilere göre gruplandırılmış bahisler
            
        Usage:
            >>> bets_service = OddsLiveBetsService()
            >>> categories = bets_service.get_bets_by_category()
            >>> print(f"Categories: {list(categories.keys())}")
        """
        bets = self.get_all_bets(timeout=timeout)
        
        categories = {
            'Over/Under': [],
            'Asian Handicap': [],
            'Corners': [],
            'Goal Scorers': [],
            'Half Time': [],
            'Extra Time': [],
            'Penalties': [],
            'Match Result': [],
            'Other': []
        }
        
        for bet in bets:
            name = bet.get('name', '').lower()
            categorized = False
            
            if 'over' in name or 'under' in name:
                categories['Over/Under'].append(bet)
                categorized = True
            elif 'asian' in name and 'handicap' in name:
                categories['Asian Handicap'].append(bet)
                categorized = True
            elif 'corner' in name:
                categories['Corners'].append(bet)
                categorized = True
            elif 'scorer' in name or 'score' in name:
                categories['Goal Scorers'].append(bet)
                categorized = True
            elif '1st half' in name or 'half time' in name:
                categories['Half Time'].append(bet)
                categorized = True
            elif 'extra time' in name:
                categories['Extra Time'].append(bet)
                categorized = True
            elif 'penalty' in name or 'penalties' in name:
                categories['Penalties'].append(bet)
                categorized = True
            elif '1x2' in name or 'fulltime result' in name or 'match result' in name:
                categories['Match Result'].append(bet)
                categorized = True
            
            if not categorized:
                categories['Other'].append(bet)
        
        return categories


if __name__ == "__main__":
    # Test odds live bets service
    print("Testing Odds Live Bets Service...")
    
    try:
        with OddsLiveBetsService() as service:
            # Test get all bets
            bets = service.get_all_bets()
            print(f"✓ Total live bets: {len(bets)}")
            
            # Test get bet by ID
            bet = service.get_bet_by_id("36")
            if bet:
                print(f"✓ Bet 36: {bet['name']}")
            
            # Test search bets
            over_bets = service.search_bets("Over")
            print(f"✓ Over bets found: {len(over_bets)}")
            
            # Test get over/under bets
            ou_bets = service.get_over_under_bets()
            print(f"✓ Over/Under bets: {len(ou_bets)}")
            
            # Test get corner bets
            corner_bets = service.get_corner_bets()
            print(f"✓ Corner bets: {len(corner_bets)}")
            
            # Test get bets by category
            categories = service.get_bets_by_category()
            print(f"✓ Categories: {list(categories.keys())}")
            
    except Exception as e:
        print(f"✗ Error testing odds live bets service: {e}")
