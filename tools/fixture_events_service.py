"""
API Football Fixture Events Service Module

Bu modül API Football Fixture Events endpoint'i için servis sınıfını içerir.
Maç olaylarını (gol, kart, değişiklik vb.) almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class FixtureEventsService(BaseService):
    """
    API Football Fixture Events servisi.
    
    Bu servis maç olaylarını almak için kullanılır.
    Gol, kart, değişiklik ve VAR olayları dahil olmak üzere tüm maç olayları.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        FixtureEventsService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/fixtures/events'

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

    
    def get_fixture_events(self, fixture_id: int,
                          team: Optional[int] = None,
                          player: Optional[int] = None,
                          event_type: Optional[str] = None,
                          timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Maç olaylarını alır.
        
        Args:
            fixture_id (int): Maç ID'si (zorunlu)
            team (Optional[int]): Takım ID'si
            player (Optional[int]): Oyuncu ID'si
            event_type (Optional[str]): Olay tipi ("Goal", "Card", "subst", "Var")
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> events_service = FixtureEventsService()
            >>> result = events_service.get_fixture_events(215662)
            >>> print(f"Events found: {result['results']}")
        """
        params = {'fixture': fixture_id}
        
        if team is not None:
            params['team'] = team
        
        if player is not None:
            params['player'] = player
        
        if event_type is not None:
            params['type'] = event_type
        
        return self.get(
            endpoint=self.endpoint,
            params=params,
            timeout=timeout
        )
    
    def get_all_events(self, fixture_id: int, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Maçın tüm olaylarını alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Olay listesi
            
        Usage:
            >>> events_service = FixtureEventsService()
            >>> events = events_service.get_all_events(215662)
            >>> print(f"Total events: {len(events)}")
        """
        result = self.get_fixture_events(fixture_id, timeout=timeout)
        return result.get('response', [])
    
    def get_goals(self, fixture_id: int, team: Optional[int] = None,
                 timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Maçın gollerini alır.
        
        Args:
            fixture_id (int): Maç ID'si
            team (Optional[int]): Belirli bir takımın golleri
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Gol listesi
            
        Usage:
            >>> events_service = FixtureEventsService()
            >>> goals = events_service.get_goals(215662)
            >>> print(f"Goals scored: {len(goals)}")
        """
        result = self.get_fixture_events(fixture_id, team=team, 
                                       event_type="Goal", timeout=timeout)
        return result.get('response', [])
    
    def get_cards(self, fixture_id: int, team: Optional[int] = None,
                 timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Maçın kartlarını alır.
        
        Args:
            fixture_id (int): Maç ID'si
            team (Optional[int]): Belirli bir takımın kartları
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Kart listesi
            
        Usage:
            >>> events_service = FixtureEventsService()
            >>> cards = events_service.get_cards(215662)
            >>> print(f"Cards shown: {len(cards)}")
        """
        result = self.get_fixture_events(fixture_id, team=team, 
                                       event_type="Card", timeout=timeout)
        return result.get('response', [])
    
    def get_substitutions(self, fixture_id: int, team: Optional[int] = None,
                         timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Maçın oyuncu değişikliklerini alır.
        
        Args:
            fixture_id (int): Maç ID'si
            team (Optional[int]): Belirli bir takımın değişiklikleri
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Değişiklik listesi
            
        Usage:
            >>> events_service = FixtureEventsService()
            >>> subs = events_service.get_substitutions(215662)
            >>> print(f"Substitutions made: {len(subs)}")
        """
        result = self.get_fixture_events(fixture_id, team=team, 
                                       event_type="subst", timeout=timeout)
        return result.get('response', [])
    
    def get_var_events(self, fixture_id: int, team: Optional[int] = None,
                      timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Maçın VAR olaylarını alır.
        
        Args:
            fixture_id (int): Maç ID'si
            team (Optional[int]): Belirli bir takımın VAR olayları
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: VAR olay listesi
            
        Note:
            VAR olayları 2020-2021 sezonundan itibaren mevcuttur.
            
        Usage:
            >>> events_service = FixtureEventsService()
            >>> var_events = events_service.get_var_events(215662)
            >>> print(f"VAR events: {len(var_events)}")
        """
        result = self.get_fixture_events(fixture_id, team=team, 
                                       event_type="Var", timeout=timeout)
        return result.get('response', [])
    
    def get_player_events(self, fixture_id: int, player_id: int,
                         timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir oyuncunun maçtaki olaylarını alır.
        
        Args:
            fixture_id (int): Maç ID'si
            player_id (int): Oyuncu ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Oyuncunun olayları
            
        Usage:
            >>> events_service = FixtureEventsService()
            >>> player_events = events_service.get_player_events(215662, 6126)
            >>> print(f"Player events: {len(player_events)}")
        """
        result = self.get_fixture_events(fixture_id, player=player_id, timeout=timeout)
        return result.get('response', [])
    
    def get_events_by_half(self, fixture_id: int, half: int,
                          timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir yarıdaki olayları alır.
        
        Args:
            fixture_id (int): Maç ID'si
            half (int): Yarı (1 veya 2)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Belirtilen yarıdaki olaylar
            
        Usage:
            >>> events_service = FixtureEventsService()
            >>> first_half = events_service.get_events_by_half(215662, 1)
            >>> print(f"First half events: {len(first_half)}")
        """
        all_events = self.get_all_events(fixture_id, timeout=timeout)
        
        if half == 1:
            return [event for event in all_events 
                   if event.get('time', {}).get('elapsed', 0) <= 45]
        elif half == 2:
            return [event for event in all_events 
                   if event.get('time', {}).get('elapsed', 0) > 45]
        else:
            return []
    
    def get_yellow_cards(self, fixture_id: int, team: Optional[int] = None,
                        timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Sarı kartları alır.
        
        Args:
            fixture_id (int): Maç ID'si
            team (Optional[int]): Belirli bir takımın sarı kartları
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Sarı kart listesi
            
        Usage:
            >>> events_service = FixtureEventsService()
            >>> yellow_cards = events_service.get_yellow_cards(215662)
            >>> print(f"Yellow cards: {len(yellow_cards)}")
        """
        cards = self.get_cards(fixture_id, team=team, timeout=timeout)
        return [card for card in cards 
                if card.get('detail') == 'Yellow Card']
    
    def get_red_cards(self, fixture_id: int, team: Optional[int] = None,
                     timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Kırmızı kartları alır.
        
        Args:
            fixture_id (int): Maç ID'si
            team (Optional[int]): Belirli bir takımın kırmızı kartları
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Kırmızı kart listesi
            
        Usage:
            >>> events_service = FixtureEventsService()
            >>> red_cards = events_service.get_red_cards(215662)
            >>> print(f"Red cards: {len(red_cards)}")
        """
        cards = self.get_cards(fixture_id, team=team, timeout=timeout)
        return [card for card in cards 
                if card.get('detail') == 'Red Card']


if __name__ == "__main__":
    # Test fixture events service
    print("Testing Fixture Events Service...")
    
    try:
        with FixtureEventsService() as service:
            # Test get all events
            events = service.get_all_events(215662)
            print(f"✓ Total events: {len(events)}")
            
            # Test get goals
            goals = service.get_goals(215662)
            print(f"✓ Goals: {len(goals)}")
            
            # Test get cards
            cards = service.get_cards(215662)
            print(f"✓ Cards: {len(cards)}")
            
            # Test get substitutions
            subs = service.get_substitutions(215662)
            print(f"✓ Substitutions: {len(subs)}")
            
            # Test get yellow cards
            yellow_cards = service.get_yellow_cards(215662)
            print(f"✓ Yellow cards: {len(yellow_cards)}")
            
            # Test get red cards
            red_cards = service.get_red_cards(215662)
            print(f"✓ Red cards: {len(red_cards)}")
            
    except Exception as e:
        print(f"✗ Error testing fixture events service: {e}")
