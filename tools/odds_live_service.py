"""
API Football Odds Live Service Module

Bu modül API Football Odds Live endpoint'i için servis sınıfını içerir.
Canlı bahis oranlarını almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class OddsLiveService(BaseService):
    """
    API Football Odds Live servisi.
    
    Bu servis canlı bahis oranlarını almak için kullanılır.
    Devam eden maçlar için anlık bahis oranları sağlar.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        OddsLiveService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/odds/live'

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

    
    def get_live_odds(self, fixture: Optional[int] = None,
                     league: Optional[int] = None,
                     bet: Optional[int] = None,
                     timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Canlı bahis oranlarını alır.
        
        Args:
            fixture (Optional[int]): Maç ID'si
            league (Optional[int]): Lig ID'si
            bet (Optional[int]): Bahis ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> odds_service = OddsLiveService()
            >>> result = odds_service.get_live_odds(fixture=721238)
            >>> print(f"Live odds found: {result['results']}")
        """
        params = {}
        
        if fixture is not None:
            params['fixture'] = fixture
        
        if league is not None:
            params['league'] = league
        
        if bet is not None:
            params['bet'] = bet
        
        return self.get(
            endpoint=self.endpoint,
            params=params,
            timeout=timeout
        )
    
    def get_fixture_live_odds(self, fixture_id: int, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir maçın canlı bahis oranlarını alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Maç bahis oranları, bulunamazsa None
            
        Usage:
            >>> odds_service = OddsLiveService()
            >>> odds = odds_service.get_fixture_live_odds(721238)
            >>> if odds:
            ...     print(f"Fixture status: {odds['fixture']['status']['long']}")
        """
        result = self.get_live_odds(fixture=fixture_id, timeout=timeout)
        odds_data = result.get('response', [])
        return odds_data[0] if odds_data else None
    
    def get_all_live_odds(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Tüm canlı bahis oranlarını alır.
        
        Args:
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Tüm canlı bahis oranları
            
        Usage:
            >>> odds_service = OddsLiveService()
            >>> all_odds = odds_service.get_all_live_odds()
            >>> print(f"Live fixtures with odds: {len(all_odds)}")
        """
        result = self.get_live_odds(timeout=timeout)
        return result.get('response', [])
    
    def get_league_live_odds(self, league_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir ligin canlı bahis oranlarını alır.
        
        Args:
            league_id (int): Lig ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Lig canlı bahis oranları
            
        Usage:
            >>> odds_service = OddsLiveService()
            >>> league_odds = odds_service.get_league_live_odds(39)
            >>> print(f"Premier League live odds: {len(league_odds)}")
        """
        result = self.get_live_odds(league=league_id, timeout=timeout)
        return result.get('response', [])
    
    def get_bet_type_odds(self, bet_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir bahis türünün canlı oranlarını alır.
        
        Args:
            bet_id (int): Bahis ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Bahis türü canlı oranları
            
        Usage:
            >>> odds_service = OddsLiveService()
            >>> bet_odds = odds_service.get_bet_type_odds(36)
            >>> print(f"Over/Under odds: {len(bet_odds)}")
        """
        result = self.get_live_odds(bet=bet_id, timeout=timeout)
        return result.get('response', [])
    
    def get_fixture_status(self, fixture_id: int, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Maçın canlı durumunu alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Maç durumu, bulunamazsa None
            
        Usage:
            >>> odds_service = OddsLiveService()
            >>> status = odds_service.get_fixture_status(721238)
            >>> if status:
            ...     print(f"Stopped: {status['stopped']}, Blocked: {status['blocked']}")
        """
        odds_data = self.get_fixture_live_odds(fixture_id, timeout=timeout)
        return odds_data.get('status') if odds_data else None
    
    def get_main_odds_only(self, fixture_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Maçın ana bahis oranlarını alır (main=True olanlar).
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Ana bahis oranları
            
        Usage:
            >>> odds_service = OddsLiveService()
            >>> main_odds = odds_service.get_main_odds_only(721238)
            >>> print(f"Main odds: {len(main_odds)}")
        """
        odds_data = self.get_fixture_live_odds(fixture_id, timeout=timeout)
        if not odds_data:
            return []
        
        main_odds = []
        for bet in odds_data.get('odds', []):
            main_values = [value for value in bet.get('values', []) 
                          if value.get('main') is True]
            if main_values:
                main_bet = {
                    'id': bet.get('id'),
                    'name': bet.get('name'),
                    'values': main_values
                }
                main_odds.append(main_bet)
        
        return main_odds
    
    def get_suspended_bets(self, fixture_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Askıya alınmış bahisleri alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Askıya alınmış bahisler
            
        Usage:
            >>> odds_service = OddsLiveService()
            >>> suspended = odds_service.get_suspended_bets(721238)
            >>> print(f"Suspended bets: {len(suspended)}")
        """
        odds_data = self.get_fixture_live_odds(fixture_id, timeout=timeout)
        if not odds_data:
            return []
        
        suspended_bets = []
        for bet in odds_data.get('odds', []):
            suspended_values = [value for value in bet.get('values', []) 
                               if value.get('suspended') is True]
            if suspended_values:
                suspended_bet = {
                    'id': bet.get('id'),
                    'name': bet.get('name'),
                    'values': suspended_values
                }
                suspended_bets.append(suspended_bet)
        
        return suspended_bets
    
    def get_over_under_odds(self, fixture_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Over/Under bahis oranlarını alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Over/Under oranları
            
        Usage:
            >>> odds_service = OddsLiveService()
            >>> ou_odds = odds_service.get_over_under_odds(721238)
            >>> print(f"Over/Under odds: {len(ou_odds)}")
        """
        odds_data = self.get_fixture_live_odds(fixture_id, timeout=timeout)
        if not odds_data:
            return []
        
        return [bet for bet in odds_data.get('odds', []) 
                if 'over' in bet.get('name', '').lower() or 'under' in bet.get('name', '').lower()]
    
    def get_asian_handicap_odds(self, fixture_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Asian Handicap bahis oranlarını alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Asian Handicap oranları
            
        Usage:
            >>> odds_service = OddsLiveService()
            >>> ah_odds = odds_service.get_asian_handicap_odds(721238)
            >>> print(f"Asian Handicap odds: {len(ah_odds)}")
        """
        odds_data = self.get_fixture_live_odds(fixture_id, timeout=timeout)
        if not odds_data:
            return []
        
        return [bet for bet in odds_data.get('odds', []) 
                if 'asian' in bet.get('name', '').lower() or 'handicap' in bet.get('name', '').lower()]
    
    def is_fixture_blocked(self, fixture_id: int, timeout: Optional[int] = None) -> bool:
        """
        Maçın bahislerinin bloke olup olmadığını kontrol eder.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            bool: Bloke ise True, değilse False
            
        Usage:
            >>> odds_service = OddsLiveService()
            >>> is_blocked = odds_service.is_fixture_blocked(721238)
            >>> print(f"Fixture blocked: {is_blocked}")
        """
        status = self.get_fixture_status(fixture_id, timeout=timeout)
        return status.get('blocked', False) if status else False
    
    def is_fixture_stopped(self, fixture_id: int, timeout: Optional[int] = None) -> bool:
        """
        Maçın durdurulup durdurulmadığını kontrol eder.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            bool: Durdurulmuş ise True, değilse False
            
        Usage:
            >>> odds_service = OddsLiveService()
            >>> is_stopped = odds_service.is_fixture_stopped(721238)
            >>> print(f"Fixture stopped: {is_stopped}")
        """
        status = self.get_fixture_status(fixture_id, timeout=timeout)
        return status.get('stopped', False) if status else False
    
    def get_best_odds(self, fixture_id: int, bet_name: str, value: str,
                     timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir bahis için en iyi oranı bulur.
        
        Args:
            fixture_id (int): Maç ID'si
            bet_name (str): Bahis adı
            value (str): Bahis değeri
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: En iyi oran, bulunamazsa None
            
        Usage:
            >>> odds_service = OddsLiveService()
            >>> best = odds_service.get_best_odds(721238, "Over/Under Line", "Over")
            >>> if best:
            ...     print(f"Best Over odd: {best['odd']}")
        """
        odds_data = self.get_fixture_live_odds(fixture_id, timeout=timeout)
        if not odds_data:
            return None
        
        best_odd = None
        best_value = 0
        
        for bet in odds_data.get('odds', []):
            if bet.get('name') == bet_name:
                for odd_value in bet.get('values', []):
                    if (odd_value.get('value') == value and 
                        not odd_value.get('suspended', False)):
                        try:
                            current_odd = float(odd_value.get('odd', 0))
                            if current_odd > best_value:
                                best_value = current_odd
                                best_odd = odd_value
                        except (ValueError, TypeError):
                            continue
        
        return best_odd


if __name__ == "__main__":
    # Test odds live service
    print("Testing Odds Live Service...")
    
    try:
        with OddsLiveService() as service:
            # Test get all live odds
            all_odds = service.get_all_live_odds()
            print(f"✓ Live fixtures with odds: {len(all_odds)}")
            
            # Test get fixture live odds
            if all_odds:
                fixture_id = all_odds[0]['fixture']['id']
                fixture_odds = service.get_fixture_live_odds(fixture_id)
                if fixture_odds:
                    print(f"✓ Fixture {fixture_id} odds found")
                
                # Test get fixture status
                status = service.get_fixture_status(fixture_id)
                if status:
                    print(f"✓ Fixture status - Blocked: {status.get('blocked')}, Stopped: {status.get('stopped')}")
                
                # Test get main odds only
                main_odds = service.get_main_odds_only(fixture_id)
                print(f"✓ Main odds: {len(main_odds)}")
                
                # Test get over/under odds
                ou_odds = service.get_over_under_odds(fixture_id)
                print(f"✓ Over/Under odds: {len(ou_odds)}")
            
    except Exception as e:
        print(f"✗ Error testing odds live service: {e}")
