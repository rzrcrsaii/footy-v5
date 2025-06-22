"""
API Football Player Profiles Service Module

Bu modül API Football Player Profiles endpoint'i için servis sınıfını içerir.
Oyuncu profil bilgilerini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from .base_service import BaseService
from .api_config import APIConfig


class PlayerProfilesService(BaseService):
    """
    API Football Player Profiles servisi.
    
    Bu servis oyuncu profil bilgilerini almak için kullanılır.
    Sayfalama sistemi kullanır (250 sonuç/sayfa).
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        PlayerProfilesService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/players/profiles'

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

    
    def get_player_profiles(self, player_id: Optional[int] = None,
                           search: Optional[str] = None,
                           page: int = 1,
                           timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Oyuncu profil bilgilerini alır.
        
        Args:
            player_id (Optional[int]): Oyuncu ID'si
            search (Optional[str]): Oyuncu soyadı (min 3 karakter)
            page (int): Sayfa numarası (varsayılan: 1)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            ValueError: search 3 karakterden kısaysa
            
        Usage:
            >>> profiles_service = PlayerProfilesService()
            >>> result = profiles_service.get_player_profiles(player_id=276)
            >>> print(f"Profiles found: {result['results']}")
        """
        params = {'page': page}
        
        if player_id is not None:
            params['player'] = player_id
        
        if search is not None:
            if len(search) < 3:
                raise ValueError("Search term must be at least 3 characters")
            params['search'] = search
        
        return self.get(
            endpoint=self.endpoint,
            params=params,
            timeout=timeout
        )
    
    def get_player_by_id(self, player_id: int, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir oyuncunun profil bilgilerini alır.
        
        Args:
            player_id (int): Oyuncu ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Oyuncu profili, bulunamazsa None
            
        Usage:
            >>> profiles_service = PlayerProfilesService()
            >>> player = profiles_service.get_player_by_id(276)
            >>> if player:
            ...     print(f"Player: {player['player']['name']}")
        """
        result = self.get_player_profiles(player_id=player_id, timeout=timeout)
        profiles = result.get('response', [])
        return profiles[0] if profiles else None
    
    def search_players(self, lastname: str, page: int = 1,
                      timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Oyuncu soyadına göre arama yapar.
        
        Args:
            lastname (str): Oyuncu soyadı (min 3 karakter)
            page (int): Sayfa numarası (varsayılan: 1)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Bulunan oyuncular
            
        Usage:
            >>> profiles_service = PlayerProfilesService()
            >>> players = profiles_service.search_players("Silva")
            >>> print(f"Players found: {len(players)}")
        """
        result = self.get_player_profiles(search=lastname, page=page, timeout=timeout)
        return result.get('response', [])
    
    def get_all_players(self, max_pages: int = 10, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Tüm oyuncuları alır (sayfalama ile).
        
        Args:
            max_pages (int): Maksimum sayfa sayısı (varsayılan: 10)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Oyuncu listesi
            
        Warning:
            Bu fonksiyon çok fazla API çağrısı yapabilir. Dikkatli kullanın.
            
        Usage:
            >>> profiles_service = PlayerProfilesService()
            >>> players = profiles_service.get_all_players(max_pages=2)
            >>> print(f"Total players: {len(players)}")
        """
        all_players = []
        page = 1
        
        while page <= max_pages:
            result = self.get_player_profiles(page=page, timeout=timeout)
            players = result.get('response', [])
            
            if not players:
                break
            
            all_players.extend(players)
            
            # Sayfa bilgisini kontrol et
            paging = result.get('paging', {})
            if page >= paging.get('total', 1):
                break
            
            page += 1
        
        return all_players
    
    def get_player_photo_url(self, player_id: int) -> str:
        """
        Oyuncu fotoğrafı URL'ini oluşturur.
        
        Args:
            player_id (int): Oyuncu ID'si
            
        Returns:
            str: Fotoğraf URL'i
            
        Usage:
            >>> profiles_service = PlayerProfilesService()
            >>> photo_url = profiles_service.get_player_photo_url(276)
            >>> print(f"Photo URL: {photo_url}")
        """
        return f"https://media.api-sports.io/football/players/{player_id}.png"
    
    def get_player_basic_info(self, player_id: int, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Oyuncunun temel bilgilerini alır.
        
        Args:
            player_id (int): Oyuncu ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Temel bilgiler, bulunamazsa None
            
        Usage:
            >>> profiles_service = PlayerProfilesService()
            >>> info = profiles_service.get_player_basic_info(276)
            >>> if info:
            ...     print(f"Name: {info['name']}, Age: {info['age']}")
        """
        player_data = self.get_player_by_id(player_id, timeout=timeout)
        return player_data.get('player') if player_data else None
    
    def get_players_by_nationality(self, nationality: str, max_pages: int = 5,
                                  timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir milliyetteki oyuncuları alır.
        
        Args:
            nationality (str): Milliyet
            max_pages (int): Maksimum sayfa sayısı (varsayılan: 5)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Belirtilen milliyetteki oyuncular
            
        Usage:
            >>> profiles_service = PlayerProfilesService()
            >>> brazilians = profiles_service.get_players_by_nationality("Brazil", 2)
            >>> print(f"Brazilian players: {len(brazilians)}")
        """
        all_players = self.get_all_players(max_pages=max_pages, timeout=timeout)
        
        return [player for player in all_players 
                if player.get('player', {}).get('nationality', '').lower() == nationality.lower()]
    
    def get_players_by_position(self, position: str, max_pages: int = 5,
                               timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli pozisyondaki oyuncuları alır.
        
        Args:
            position (str): Pozisyon (örn: "Goalkeeper", "Defender", "Midfielder", "Attacker")
            max_pages (int): Maksimum sayfa sayısı (varsayılan: 5)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Belirtilen pozisyondaki oyuncular
            
        Usage:
            >>> profiles_service = PlayerProfilesService()
            >>> goalkeepers = profiles_service.get_players_by_position("Goalkeeper", 2)
            >>> print(f"Goalkeepers: {len(goalkeepers)}")
        """
        all_players = self.get_all_players(max_pages=max_pages, timeout=timeout)
        
        return [player for player in all_players 
                if player.get('player', {}).get('position', '').lower() == position.lower()]
    
    def get_players_by_age_range(self, min_age: int, max_age: int, max_pages: int = 5,
                                timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli yaş aralığındaki oyuncuları alır.
        
        Args:
            min_age (int): Minimum yaş
            max_age (int): Maksimum yaş
            max_pages (int): Maksimum sayfa sayısı (varsayılan: 5)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Belirtilen yaş aralığındaki oyuncular
            
        Usage:
            >>> profiles_service = PlayerProfilesService()
            >>> young_players = profiles_service.get_players_by_age_range(18, 25, 2)
            >>> print(f"Young players (18-25): {len(young_players)}")
        """
        all_players = self.get_all_players(max_pages=max_pages, timeout=timeout)
        
        return [player for player in all_players 
                if min_age <= player.get('player', {}).get('age', 0) <= max_age]
    
    def get_player_birth_info(self, player_id: int, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Oyuncunun doğum bilgilerini alır.
        
        Args:
            player_id (int): Oyuncu ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Doğum bilgileri, bulunamazsa None
            
        Usage:
            >>> profiles_service = PlayerProfilesService()
            >>> birth_info = profiles_service.get_player_birth_info(276)
            >>> if birth_info:
            ...     print(f"Born: {birth_info['date']} in {birth_info['place']}")
        """
        player_data = self.get_player_by_id(player_id, timeout=timeout)
        if player_data:
            return player_data.get('player', {}).get('birth')
        return None
    
    def get_player_physical_stats(self, player_id: int, timeout: Optional[int] = None) -> Optional[Dict[str, str]]:
        """
        Oyuncunun fiziksel özelliklerini alır.
        
        Args:
            player_id (int): Oyuncu ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, str]]: Fiziksel özellikler, bulunamazsa None
            
        Usage:
            >>> profiles_service = PlayerProfilesService()
            >>> physical = profiles_service.get_player_physical_stats(276)
            >>> if physical:
            ...     print(f"Height: {physical['height']}, Weight: {physical['weight']}")
        """
        player_data = self.get_player_by_id(player_id, timeout=timeout)
        if player_data:
            player_info = player_data.get('player', {})
            return {
                'height': player_info.get('height'),
                'weight': player_info.get('weight')
            }
        return None


if __name__ == "__main__":
    # Test player profiles service
    print("Testing Player Profiles Service...")
    
    try:
        with PlayerProfilesService() as service:
            # Test get player by ID
            player = service.get_player_by_id(276)
            if player:
                print(f"✓ Player found: {player['player']['name']}")
            
            # Test search players
            players = service.search_players("Silva")
            print(f"✓ Players with lastname Silva: {len(players)}")
            
            # Test get player photo URL
            photo_url = service.get_player_photo_url(276)
            print(f"✓ Photo URL: {photo_url}")
            
            # Test get player basic info
            info = service.get_player_basic_info(276)
            if info:
                print(f"✓ Player info - Age: {info.get('age')}, Position: {info.get('position')}")
            
            # Test get birth info
            birth_info = service.get_player_birth_info(276)
            if birth_info:
                print(f"✓ Birth info - Date: {birth_info.get('date')}, Place: {birth_info.get('place')}")
            
    except Exception as e:
        print(f"✗ Error testing player profiles service: {e}")
