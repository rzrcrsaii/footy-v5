"""
API Football Prematch Odds Service Module

Bu modül API Football Prematch Odds endpoint'i için servis sınıfını içerir.
Maç öncesi bahis oranlarını almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
from .base_service import BaseService
from .api_config import APIConfig


class PrematchOddsService(BaseService):
    """
    API Football Prematch Odds servisi.
    
    Bu servis maç öncesi bahis oranlarını almak için kullanılır.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        PrematchOddsService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/odds'

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

    
    def get_prematch_odds(self, fixture: Optional[int] = None,
                         league: Optional[int] = None,
                         season: Optional[int] = None,
                         date: Optional[Union[str, date]] = None,
                         timezone: Optional[str] = None,
                         page: int = 1,
                         bookmaker: Optional[int] = None,
                         bet: Optional[int] = None,
                         timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Maç öncesi bahis oranlarını alır.
        
        Args:
            fixture (Optional[int]): Maç ID'si
            league (Optional[int]): Lig ID'si
            season (Optional[int]): Sezon (YYYY formatında)
            date (Optional[Union[str, date]]): Tarih (YYYY-MM-DD)
            timezone (Optional[str]): Zaman dilimi
            page (int): Sayfa numarası (varsayılan: 1)
            bookmaker (Optional[int]): Bahisçi ID'si
            bet (Optional[int]): Bahis ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> odds_service = PrematchOddsService()
            >>> result = odds_service.get_prematch_odds(fixture=198772)
            >>> print(f"Prematch odds found: {result['results']}")
        """
        params = {'page': page}
        
        if fixture is not None:
            params['fixture'] = fixture
        
        if league is not None:
            params['league'] = league
        
        if season is not None:
            params['season'] = season
        
        if date is not None:
            if isinstance(date, datetime):
                params['date'] = date.strftime('%Y-%m-%d')
            elif isinstance(date, str):
                params['date'] = date
        
        if timezone is not None:
            params['timezone'] = timezone
        
        if bookmaker is not None:
            params['bookmaker'] = bookmaker
        
        if bet is not None:
            params['bet'] = bet
        
        return self.get(
            endpoint=self.endpoint,
            params=params,
            timeout=timeout
        )
    
    def get_fixture_odds(self, fixture_id: int, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir maçın bahis oranlarını alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Maç bahis oranları, bulunamazsa None
            
        Usage:
            >>> odds_service = PrematchOddsService()
            >>> odds = odds_service.get_fixture_odds(198772)
            >>> if odds:
            ...     print(f"Bookmakers: {len(odds['bookmakers'])}")
        """
        result = self.get_prematch_odds(fixture=fixture_id, timeout=timeout)
        odds_data = result.get('response', [])
        return odds_data[0] if odds_data else None
    
    def get_league_odds(self, league_id: int, season: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir lig ve sezondaki bahis oranlarını alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Lig bahis oranları
            
        Usage:
            >>> odds_service = PrematchOddsService()
            >>> odds = odds_service.get_league_odds(39, 2023)
            >>> print(f"Premier League odds: {len(odds)}")
        """
        all_odds = []
        page = 1
        
        while True:
            result = self.get_prematch_odds(league=league_id, season=season, 
                                          page=page, timeout=timeout)
            odds = result.get('response', [])
            
            if not odds:
                break
            
            all_odds.extend(odds)
            
            # Sayfa bilgisini kontrol et
            paging = result.get('paging', {})
            if page >= paging.get('total', 1):
                break
            
            page += 1
        
        return all_odds
    
    def get_odds_by_date(self, odds_date: Union[str, date], timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir tarihteki bahis oranlarını alır.
        
        Args:
            odds_date (Union[str, date]): Tarih (YYYY-MM-DD formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Tarih bazlı bahis oranları
            
        Usage:
            >>> odds_service = PrematchOddsService()
            >>> odds = odds_service.get_odds_by_date("2023-12-25")
            >>> print(f"Christmas odds: {len(odds)}")
        """
        result = self.get_prematch_odds(date=odds_date, timeout=timeout)
        return result.get('response', [])
    
    def get_bookmaker_odds(self, fixture_id: int, bookmaker_id: int,
                          timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir bahisçinin maç oranlarını alır.
        
        Args:
            fixture_id (int): Maç ID'si
            bookmaker_id (int): Bahisçi ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Bahisçi oranları, bulunamazsa None
            
        Usage:
            >>> odds_service = PrematchOddsService()
            >>> odds = odds_service.get_bookmaker_odds(198772, 6)
            >>> if odds:
            ...     print(f"Bet365 odds available")
        """
        result = self.get_prematch_odds(fixture=fixture_id, bookmaker=bookmaker_id, timeout=timeout)
        odds_data = result.get('response', [])
        return odds_data[0] if odds_data else None
    
    def get_bet_type_odds(self, fixture_id: int, bet_id: int,
                         timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir bahis türünün oranlarını alır.
        
        Args:
            fixture_id (int): Maç ID'si
            bet_id (int): Bahis ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Bahis türü oranları, bulunamazsa None
            
        Usage:
            >>> odds_service = PrematchOddsService()
            >>> odds = odds_service.get_bet_type_odds(198772, 1)
            >>> if odds:
            ...     print(f"Match Winner odds available")
        """
        result = self.get_prematch_odds(fixture=fixture_id, bet=bet_id, timeout=timeout)
        odds_data = result.get('response', [])
        return odds_data[0] if odds_data else None
    
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
            >>> odds_service = PrematchOddsService()
            >>> best = odds_service.get_best_odds(198772, "Match Winner", "Home")
            >>> if best:
            ...     print(f"Best Home odd: {best['odd']}")
        """
        odds_data = self.get_fixture_odds(fixture_id, timeout=timeout)
        if not odds_data:
            return None
        
        best_odd = None
        best_value = 0
        
        for bookmaker in odds_data.get('bookmakers', []):
            for bet in bookmaker.get('bets', []):
                if bet.get('name') == bet_name:
                    for odd_value in bet.get('values', []):
                        if odd_value.get('value') == value:
                            try:
                                current_odd = float(odd_value.get('odd', 0))
                                if current_odd > best_value:
                                    best_value = current_odd
                                    best_odd = {
                                        'bookmaker': bookmaker.get('name'),
                                        'bookmaker_id': bookmaker.get('id'),
                                        'bet_name': bet_name,
                                        'value': value,
                                        'odd': current_odd
                                    }
                            except (ValueError, TypeError):
                                continue
        
        return best_odd
    
    def compare_bookmaker_odds(self, fixture_id: int, bet_name: str, value: str,
                              timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Farklı bahisçilerin aynı bahis için oranlarını karşılaştırır.
        
        Args:
            fixture_id (int): Maç ID'si
            bet_name (str): Bahis adı
            value (str): Bahis değeri
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Bahisçi oranları karşılaştırması
            
        Usage:
            >>> odds_service = PrematchOddsService()
            >>> comparison = odds_service.compare_bookmaker_odds(198772, "Match Winner", "Home")
            >>> print(f"Bookmakers offering Home odds: {len(comparison)}")
        """
        odds_data = self.get_fixture_odds(fixture_id, timeout=timeout)
        if not odds_data:
            return []
        
        comparisons = []
        
        for bookmaker in odds_data.get('bookmakers', []):
            for bet in bookmaker.get('bets', []):
                if bet.get('name') == bet_name:
                    for odd_value in bet.get('values', []):
                        if odd_value.get('value') == value:
                            try:
                                odd_float = float(odd_value.get('odd', 0))
                                comparisons.append({
                                    'bookmaker': bookmaker.get('name'),
                                    'bookmaker_id': bookmaker.get('id'),
                                    'odd': odd_float
                                })
                            except (ValueError, TypeError):
                                continue
        
        # Orana göre sırala (yüksekten düşüğe)
        comparisons.sort(key=lambda x: x['odd'], reverse=True)
        return comparisons
    
    def get_available_bookmakers(self, fixture_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Maç için mevcut bahisçileri listeler.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Mevcut bahisçiler
            
        Usage:
            >>> odds_service = PrematchOddsService()
            >>> bookmakers = odds_service.get_available_bookmakers(198772)
            >>> print(f"Available bookmakers: {len(bookmakers)}")
        """
        odds_data = self.get_fixture_odds(fixture_id, timeout=timeout)
        if not odds_data:
            return []
        
        bookmakers = []
        for bookmaker in odds_data.get('bookmakers', []):
            bookmakers.append({
                'id': bookmaker.get('id'),
                'name': bookmaker.get('name'),
                'bets_count': len(bookmaker.get('bets', []))
            })
        
        return bookmakers
    
    def get_available_bet_types(self, fixture_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Maç için mevcut bahis türlerini listeler.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Mevcut bahis türleri
            
        Usage:
            >>> odds_service = PrematchOddsService()
            >>> bet_types = odds_service.get_available_bet_types(198772)
            >>> print(f"Available bet types: {len(bet_types)}")
        """
        odds_data = self.get_fixture_odds(fixture_id, timeout=timeout)
        if not odds_data:
            return []
        
        bet_types = set()
        for bookmaker in odds_data.get('bookmakers', []):
            for bet in bookmaker.get('bets', []):
                bet_types.add((bet.get('id'), bet.get('name')))
        
        return [{'id': bet_id, 'name': bet_name} for bet_id, bet_name in bet_types]


if __name__ == "__main__":
    # Test prematch odds service
    print("Testing Prematch Odds Service...")
    
    try:
        with PrematchOddsService() as service:
            # Test get fixture odds
            odds = service.get_fixture_odds(198772)
            if odds:
                print(f"✓ Fixture odds found - Bookmakers: {len(odds.get('bookmakers', []))}")
            
            # Test get available bookmakers
            bookmakers = service.get_available_bookmakers(198772)
            print(f"✓ Available bookmakers: {len(bookmakers)}")
            
            # Test get available bet types
            bet_types = service.get_available_bet_types(198772)
            print(f"✓ Available bet types: {len(bet_types)}")
            
            # Test get best odds
            best = service.get_best_odds(198772, "Match Winner", "Home")
            if best:
                print(f"✓ Best Home odd: {best['odd']} from {best['bookmaker']}")
            
            # Test compare bookmaker odds
            comparison = service.compare_bookmaker_odds(198772, "Match Winner", "Home")
            print(f"✓ Bookmaker comparison: {len(comparison)} offers")
            
    except Exception as e:
        print(f"✗ Error testing prematch odds service: {e}")
