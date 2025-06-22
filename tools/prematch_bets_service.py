"""
API Football Prematch Bets Service Module

Bu modül API Football Prematch Bets endpoint'i için servis sınıfını içerir.
Maç öncesi bahis türlerini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class PrematchBetsService(BaseService):
    """
    API Football Prematch Bets servisi.
    
    Bu servis maç öncesi bahis türlerini almak için kullanılır.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        PrematchBetsService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/odds/bets'

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

    
    def get_prematch_bets(self, bet_id: Optional[str] = None,
                         search: Optional[str] = None,
                         timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Maç öncesi bahis türlerini alır.
        
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
            >>> bets_service = PrematchBetsService()
            >>> result = bets_service.get_prematch_bets()
            >>> print(f"Prematch bets found: {result['results']}")
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
        Tüm maç öncesi bahis türlerini alır.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Bahis türleri listesi
            
        Usage:
            >>> bets_service = PrematchBetsService()
            >>> bets = bets_service.get_all_bets()
            >>> print(f"Total prematch bets: {len(bets)}")
        """
        result = self.get_prematch_bets(timeout=timeout)
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
            >>> bets_service = PrematchBetsService()
            >>> bet = bets_service.get_bet_by_id("1")
            >>> if bet:
            ...     print(f"Bet: {bet['name']}")
        """
        result = self.get_prematch_bets(bet_id=bet_id, timeout=timeout)
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
            >>> bets_service = PrematchBetsService()
            >>> bets = bets_service.search_bets("Match")
            >>> print(f"Match bets: {len(bets)}")
        """
        result = self.get_prematch_bets(search=search_term, timeout=timeout)
        return result.get('response', [])
    
    def get_bet_names(self, timeout: Optional[int] = None) -> List[str]:
        """
        Tüm bahis türü adlarını liste olarak döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[str]: Bahis türü adları
            
        Usage:
            >>> bets_service = PrematchBetsService()
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
            >>> bets_service = PrematchBetsService()
            >>> ids = bets_service.get_bet_ids()
            >>> print(f"Bet IDs: {ids[:10]}")  # İlk 10 ID
        """
        bets = self.get_all_bets(timeout=timeout)
        return [bet.get('id') for bet in bets if bet.get('id') is not None]
    
    def get_match_winner_bets(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Maç kazananı türü bahisleri filtreler.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Maç kazananı bahis türleri
            
        Usage:
            >>> bets_service = PrematchBetsService()
            >>> winner_bets = bets_service.get_match_winner_bets()
            >>> print(f"Match winner bets: {len(winner_bets)}")
        """
        bets = self.get_all_bets(timeout=timeout)
        return [bet for bet in bets 
                if 'match winner' in bet.get('name', '').lower() or 
                   '1x2' in bet.get('name', '').lower() or
                   'fulltime result' in bet.get('name', '').lower()]
    
    def get_over_under_bets(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Over/Under türü bahisleri filtreler.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Over/Under bahis türleri
            
        Usage:
            >>> bets_service = PrematchBetsService()
            >>> ou_bets = bets_service.get_over_under_bets()
            >>> print(f"Over/Under bets: {len(ou_bets)}")
        """
        bets = self.get_all_bets(timeout=timeout)
        return [bet for bet in bets 
                if 'over' in bet.get('name', '').lower() or 'under' in bet.get('name', '').lower()]
    
    def get_both_teams_score_bets(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Her iki takım gol atar türü bahisleri filtreler.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: BTTS bahis türleri
            
        Usage:
            >>> bets_service = PrematchBetsService()
            >>> btts_bets = bets_service.get_both_teams_score_bets()
            >>> print(f"BTTS bets: {len(btts_bets)}")
        """
        bets = self.get_all_bets(timeout=timeout)
        return [bet for bet in bets 
                if 'both teams' in bet.get('name', '').lower() and 'score' in bet.get('name', '').lower()]
    
    def get_handicap_bets(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Handicap türü bahisleri filtreler.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Handicap bahis türleri
            
        Usage:
            >>> bets_service = PrematchBetsService()
            >>> handicap_bets = bets_service.get_handicap_bets()
            >>> print(f"Handicap bets: {len(handicap_bets)}")
        """
        bets = self.get_all_bets(timeout=timeout)
        return [bet for bet in bets 
                if 'handicap' in bet.get('name', '').lower()]
    
    def get_correct_score_bets(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Doğru skor türü bahisleri filtreler.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Doğru skor bahis türleri
            
        Usage:
            >>> bets_service = PrematchBetsService()
            >>> score_bets = bets_service.get_correct_score_bets()
            >>> print(f"Correct score bets: {len(score_bets)}")
        """
        bets = self.get_all_bets(timeout=timeout)
        return [bet for bet in bets 
                if 'correct score' in bet.get('name', '').lower() or 
                   'exact score' in bet.get('name', '').lower()]
    
    def get_half_time_bets(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        İlk yarı türü bahisleri filtreler.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: İlk yarı bahis türleri
            
        Usage:
            >>> bets_service = PrematchBetsService()
            >>> ht_bets = bets_service.get_half_time_bets()
            >>> print(f"Half time bets: {len(ht_bets)}")
        """
        bets = self.get_all_bets(timeout=timeout)
        return [bet for bet in bets 
                if 'half time' in bet.get('name', '').lower() or 
                   '1st half' in bet.get('name', '').lower()]
    
    def get_double_chance_bets(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Çifte şans türü bahisleri filtreler.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Çifte şans bahis türleri
            
        Usage:
            >>> bets_service = PrematchBetsService()
            >>> dc_bets = bets_service.get_double_chance_bets()
            >>> print(f"Double chance bets: {len(dc_bets)}")
        """
        bets = self.get_all_bets(timeout=timeout)
        return [bet for bet in bets 
                if 'double chance' in bet.get('name', '').lower()]
    
    def get_bets_count(self, timeout: Optional[int] = None) -> int:
        """
        Toplam bahis türü sayısını döndürür.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            int: Toplam bahis türü sayısı
            
        Usage:
            >>> bets_service = PrematchBetsService()
            >>> count = bets_service.get_bets_count()
            >>> print(f"Total prematch bets: {count}")
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
            >>> bets_service = PrematchBetsService()
            >>> name = bets_service.get_bet_name_by_id(1)
            >>> print(f"Bet 1: {name}")
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
            >>> bets_service = PrematchBetsService()
            >>> bet_id = bets_service.get_bet_id_by_name("Match Winner")
            >>> print(f"Match Winner ID: {bet_id}")
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
            >>> bets_service = PrematchBetsService()
            >>> categories = bets_service.get_bets_by_category()
            >>> print(f"Categories: {list(categories.keys())}")
        """
        bets = self.get_all_bets(timeout=timeout)
        
        categories = {
            'Match Result': [],
            'Over/Under': [],
            'Both Teams Score': [],
            'Handicap': [],
            'Correct Score': [],
            'Half Time': [],
            'Double Chance': [],
            'Other': []
        }
        
        for bet in bets:
            name = bet.get('name', '').lower()
            categorized = False
            
            if ('match winner' in name or '1x2' in name or 
                'fulltime result' in name or 'result' in name):
                categories['Match Result'].append(bet)
                categorized = True
            elif 'over' in name or 'under' in name:
                categories['Over/Under'].append(bet)
                categorized = True
            elif 'both teams' in name and 'score' in name:
                categories['Both Teams Score'].append(bet)
                categorized = True
            elif 'handicap' in name:
                categories['Handicap'].append(bet)
                categorized = True
            elif 'correct score' in name or 'exact score' in name:
                categories['Correct Score'].append(bet)
                categorized = True
            elif 'half time' in name or '1st half' in name:
                categories['Half Time'].append(bet)
                categorized = True
            elif 'double chance' in name:
                categories['Double Chance'].append(bet)
                categorized = True
            
            if not categorized:
                categories['Other'].append(bet)
        
        return categories


if __name__ == "__main__":
    # Test prematch bets service
    print("Testing Prematch Bets Service...")
    
    try:
        with PrematchBetsService() as service:
            # Test get all bets
            bets = service.get_all_bets()
            print(f"✓ Total prematch bets: {len(bets)}")
            
            # Test get bet by ID
            bet = service.get_bet_by_id("1")
            if bet:
                print(f"✓ Bet 1: {bet['name']}")
            
            # Test search bets
            match_bets = service.search_bets("Match")
            print(f"✓ Match bets found: {len(match_bets)}")
            
            # Test get over/under bets
            ou_bets = service.get_over_under_bets()
            print(f"✓ Over/Under bets: {len(ou_bets)}")
            
            # Test get both teams score bets
            btts_bets = service.get_both_teams_score_bets()
            print(f"✓ BTTS bets: {len(btts_bets)}")
            
            # Test get bets by category
            categories = service.get_bets_by_category()
            print(f"✓ Categories: {list(categories.keys())}")
            
    except Exception as e:
        print(f"✗ Error testing prematch bets service: {e}")
