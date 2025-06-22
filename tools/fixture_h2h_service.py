"""
API Football Head to Head Service Module

Bu modül API Football Head to Head endpoint'i için servis sınıfını içerir.
İki takım arasındaki karşılaşma geçmişini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
from .base_service import BaseService
from .api_config import APIConfig


class FixtureH2HService(BaseService):
    """
    API Football Head to Head servisi.
    
    Bu servis iki takım arasındaki karşılaşma geçmişini almak için kullanılır.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        FixtureH2HService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/fixtures/headtohead'

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

    
    def get_head_to_head(self, team1_id: int, team2_id: int,
                        date: Optional[Union[str, date]] = None,
                        league: Optional[int] = None,
                        season: Optional[int] = None,
                        last: Optional[int] = None,
                        next: Optional[int] = None,
                        from_date: Optional[Union[str, date]] = None,
                        to_date: Optional[Union[str, date]] = None,
                        status: Optional[Union[str, List[str]]] = None,
                        venue: Optional[int] = None,
                        timezone: Optional[str] = None,
                        timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        İki takım arasındaki karşılaşma geçmişini alır.
        
        Args:
            team1_id (int): İlk takım ID'si
            team2_id (int): İkinci takım ID'si
            date (Optional[Union[str, date]]): Belirli bir tarih
            league (Optional[int]): Lig ID'si
            season (Optional[int]): Sezon (YYYY formatında)
            last (Optional[int]): Son X maç
            next (Optional[int]): Sonraki X maç
            from_date (Optional[Union[str, date]]): Başlangıç tarihi
            to_date (Optional[Union[str, date]]): Bitiş tarihi
            status (Optional[Union[str, List[str]]]): Maç durumu(ları)
            venue (Optional[int]): Saha ID'si
            timezone (Optional[str]): Zaman dilimi
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> h2h_service = FixtureH2HService()
            >>> result = h2h_service.get_head_to_head(33, 34, last=5)
            >>> print(f"H2H matches found: {result['results']}")
        """
        params = {'h2h': f"{team1_id}-{team2_id}"}
        
        if date is not None:
            if isinstance(date, datetime):
                params['date'] = date.strftime('%Y-%m-%d')
            elif isinstance(date, str):
                params['date'] = date
        
        if league is not None:
            params['league'] = league
        
        if season is not None:
            params['season'] = season
        
        if last is not None:
            params['last'] = last
        
        if next is not None:
            params['next'] = next
        
        if from_date is not None:
            if isinstance(from_date, datetime):
                params['from'] = from_date.strftime('%Y-%m-%d')
            elif isinstance(from_date, str):
                params['from'] = from_date
        
        if to_date is not None:
            if isinstance(to_date, datetime):
                params['to'] = to_date.strftime('%Y-%m-%d')
            elif isinstance(to_date, str):
                params['to'] = to_date
        
        if status is not None:
            if isinstance(status, str):
                params['status'] = status
            elif isinstance(status, list):
                params['status'] = '-'.join(status)
        
        if venue is not None:
            params['venue'] = venue
        
        if timezone is not None:
            params['timezone'] = timezone
        
        return self.get(
            endpoint=self.endpoint,
            params=params,
            timeout=timeout
        )
    
    def get_all_h2h_matches(self, team1_id: int, team2_id: int,
                           timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        İki takım arasındaki tüm karşılaşmaları alır.
        
        Args:
            team1_id (int): İlk takım ID'si
            team2_id (int): İkinci takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Karşılaşma listesi
            
        Usage:
            >>> h2h_service = FixtureH2HService()
            >>> matches = h2h_service.get_all_h2h_matches(33, 34)
            >>> print(f"Total H2H matches: {len(matches)}")
        """
        result = self.get_head_to_head(team1_id, team2_id, timeout=timeout)
        return result.get('response', [])
    
    def get_recent_h2h_matches(self, team1_id: int, team2_id: int, count: int = 5,
                              timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        İki takım arasındaki son karşılaşmaları alır.
        
        Args:
            team1_id (int): İlk takım ID'si
            team2_id (int): İkinci takım ID'si
            count (int): Alınacak maç sayısı (varsayılan: 5)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Son karşılaşmalar
            
        Usage:
            >>> h2h_service = FixtureH2HService()
            >>> recent = h2h_service.get_recent_h2h_matches(33, 34, 3)
            >>> print(f"Last 3 H2H matches: {len(recent)}")
        """
        result = self.get_head_to_head(team1_id, team2_id, last=count, timeout=timeout)
        return result.get('response', [])
    
    def get_h2h_by_league(self, team1_id: int, team2_id: int, league_id: int,
                         season: Optional[int] = None,
                         timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir ligdeki karşılaşmaları alır.
        
        Args:
            team1_id (int): İlk takım ID'si
            team2_id (int): İkinci takım ID'si
            league_id (int): Lig ID'si
            season (Optional[int]): Sezon (YYYY formatında)
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Ligdeki karşılaşmalar
            
        Usage:
            >>> h2h_service = FixtureH2HService()
            >>> matches = h2h_service.get_h2h_by_league(33, 34, 39, 2023)
            >>> print(f"Premier League H2H: {len(matches)}")
        """
        result = self.get_head_to_head(team1_id, team2_id, league=league_id, 
                                     season=season, timeout=timeout)
        return result.get('response', [])
    
    def get_h2h_statistics(self, team1_id: int, team2_id: int,
                          timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        İki takım arasındaki karşılaşma istatistiklerini hesaplar.
        
        Args:
            team1_id (int): İlk takım ID'si
            team2_id (int): İkinci takım ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: Karşılaşma istatistikleri
            
        Usage:
            >>> h2h_service = FixtureH2HService()
            >>> stats = h2h_service.get_h2h_statistics(33, 34)
            >>> print(f"Team1 wins: {stats['team1_wins']}")
        """
        matches = self.get_all_h2h_matches(team1_id, team2_id, timeout=timeout)
        
        team1_wins = 0
        team2_wins = 0
        draws = 0
        total_goals_team1 = 0
        total_goals_team2 = 0
        
        for match in matches:
            if match.get('fixture', {}).get('status', {}).get('short') == 'FT':
                goals = match.get('goals', {})
                home_goals = goals.get('home', 0) or 0
                away_goals = goals.get('away', 0) or 0
                
                teams = match.get('teams', {})
                home_team_id = teams.get('home', {}).get('id')
                away_team_id = teams.get('away', {}).get('id')
                
                if home_team_id == team1_id:
                    total_goals_team1 += home_goals
                    total_goals_team2 += away_goals
                    if home_goals > away_goals:
                        team1_wins += 1
                    elif away_goals > home_goals:
                        team2_wins += 1
                    else:
                        draws += 1
                elif away_team_id == team1_id:
                    total_goals_team1 += away_goals
                    total_goals_team2 += home_goals
                    if away_goals > home_goals:
                        team1_wins += 1
                    elif home_goals > away_goals:
                        team2_wins += 1
                    else:
                        draws += 1
        
        total_matches = team1_wins + team2_wins + draws
        
        return {
            'total_matches': total_matches,
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'draws': draws,
            'team1_win_percentage': (team1_wins / total_matches * 100) if total_matches > 0 else 0,
            'team2_win_percentage': (team2_wins / total_matches * 100) if total_matches > 0 else 0,
            'draw_percentage': (draws / total_matches * 100) if total_matches > 0 else 0,
            'total_goals_team1': total_goals_team1,
            'total_goals_team2': total_goals_team2,
            'average_goals_team1': (total_goals_team1 / total_matches) if total_matches > 0 else 0,
            'average_goals_team2': (total_goals_team2 / total_matches) if total_matches > 0 else 0
        }
    
    def get_h2h_at_venue(self, team1_id: int, team2_id: int, venue_id: int,
                        timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir sahada oynanan karşılaşmaları alır.
        
        Args:
            team1_id (int): İlk takım ID'si
            team2_id (int): İkinci takım ID'si
            venue_id (int): Saha ID'si
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Belirtilen sahada oynanan maçlar
            
        Usage:
            >>> h2h_service = FixtureH2HService()
            >>> matches = h2h_service.get_h2h_at_venue(33, 34, 556)
            >>> print(f"Matches at Old Trafford: {len(matches)}")
        """
        result = self.get_head_to_head(team1_id, team2_id, venue=venue_id, timeout=timeout)
        return result.get('response', [])


if __name__ == "__main__":
    # Test fixture H2H service
    print("Testing Fixture H2H Service...")
    
    try:
        with FixtureH2HService() as service:
            # Test get recent H2H matches
            recent = service.get_recent_h2h_matches(33, 34, 3)
            print(f"✓ Recent H2H matches: {len(recent)}")
            
            # Test get H2H statistics
            stats = service.get_h2h_statistics(33, 34)
            print(f"✓ H2H Statistics - Total matches: {stats['total_matches']}")
            
            # Test get H2H by league
            league_matches = service.get_h2h_by_league(33, 34, 39)
            print(f"✓ Premier League H2H: {len(league_matches)}")
            
    except Exception as e:
        print(f"✗ Error testing fixture H2H service: {e}")
