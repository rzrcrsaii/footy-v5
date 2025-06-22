"""
API Football Fixtures Service Module

Bu modül API Football Fixtures endpoint'i için servis sınıfını içerir.
Maç fikstürlerini almak için kullanılır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
from .base_service import BaseService
from .api_config import APIConfig


class FixturesService(BaseService):
    """
    API Football Fixtures servisi.
    
    Bu servis maç fikstürlerini almak için kullanılır.
    Canlı maçlar, geçmiş maçlar ve gelecek maçlar için kullanılabilir.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        FixturesService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/fixtures'

    def fetch(self, **params) -> dict:
        """
        Fetch fixtures data with given parameters.

        Args:
            **params: Fixture query parameters

        Returns:
            dict: API response
        """
        return self.get_fixtures(**params)

    def get_fixtures(self, fixture_id: Optional[int] = None,
                    fixture_ids: Optional[List[int]] = None,
                    live: Optional[Union[str, List[int]]] = None,
                    date: Optional[Union[str, date]] = None,
                    league: Optional[int] = None,
                    season: Optional[int] = None,
                    team: Optional[int] = None,
                    last: Optional[int] = None,
                    next: Optional[int] = None,
                    from_date: Optional[Union[str, date]] = None,
                    to_date: Optional[Union[str, date]] = None,
                    round_name: Optional[str] = None,
                    status: Optional[Union[str, List[str]]] = None,
                    venue: Optional[int] = None,
                    timezone: Optional[str] = None,
                    timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Maç fikstürlerini alır.
        
        Args:
            fixture_id (Optional[int]): Belirli bir maç ID'si
            fixture_ids (Optional[List[int]]): Birden fazla maç ID'si (max 20)
            live (Optional[Union[str, List[int]]]): Canlı maçlar ("all" veya lig ID'leri)
            date (Optional[Union[str, date]]): Belirli bir tarih (YYYY-MM-DD)
            league (Optional[int]): Lig ID'si
            season (Optional[int]): Sezon (YYYY formatında)
            team (Optional[int]): Takım ID'si
            last (Optional[int]): Son X maç (max 99)
            next (Optional[int]): Sonraki X maç (max 99)
            from_date (Optional[Union[str, date]]): Başlangıç tarihi
            to_date (Optional[Union[str, date]]): Bitiş tarihi
            round_name (Optional[str]): Tur adı
            status (Optional[Union[str, List[str]]]): Maç durumu(ları)
            venue (Optional[int]): Saha ID'si
            timezone (Optional[str]): Zaman dilimi
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> fixtures_service = FixturesService()
            >>> result = fixtures_service.get_fixtures(league=39, season=2023)
            >>> print(f"Fixtures found: {result['results']}")
        """
        params = {}
        
        if fixture_id is not None:
            params['id'] = fixture_id
        
        if fixture_ids:
            if len(fixture_ids) > 20:
                raise ValueError("Maximum 20 fixture IDs allowed")
            params['ids'] = '-'.join(map(str, fixture_ids))
        
        if live is not None:
            if isinstance(live, str):
                params['live'] = live
            elif isinstance(live, list):
                params['live'] = '-'.join(map(str, live))
        
        if date is not None:
            if isinstance(date, datetime):
                params['date'] = date.strftime('%Y-%m-%d')
            elif isinstance(date, str):
                params['date'] = date
        
        if league is not None:
            params['league'] = league
        
        if season is not None:
            params['season'] = season
        
        if team is not None:
            params['team'] = team
        
        if last is not None:
            if last > 99:
                raise ValueError("Maximum 99 for last parameter")
            params['last'] = last
        
        if next is not None:
            if next > 99:
                raise ValueError("Maximum 99 for next parameter")
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
        
        if round_name is not None:
            params['round'] = round_name
        
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
    
    def get_fixture_by_id(self, fixture_id: int, timezone: Optional[str] = None,
                         timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Belirli bir maçın detaylarını alır.
        
        Args:
            fixture_id (int): Maç ID'si
            timezone (Optional[str]): Zaman dilimi
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            Optional[Dict[str, Any]]: Maç detayları, bulunamazsa None
            
        Usage:
            >>> fixtures_service = FixturesService()
            >>> fixture = fixtures_service.get_fixture_by_id(239625)
            >>> if fixture:
            ...     print(f"Match: {fixture['teams']['home']['name']} vs {fixture['teams']['away']['name']}")
        """
        result = self.get_fixtures(fixture_id=fixture_id, timezone=timezone, timeout=timeout)
        fixtures = result.get('response', [])
        return fixtures[0] if fixtures else None
    
    def get_live_fixtures(self, league_ids: Optional[List[int]] = None,
                         timezone: Optional[str] = None,
                         timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Canlı maçları alır.
        
        Args:
            league_ids (Optional[List[int]]): Belirli lig ID'leri, None ise tüm canlı maçlar
            timezone (Optional[str]): Zaman dilimi
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Canlı maç listesi
            
        Usage:
            >>> fixtures_service = FixturesService()
            >>> live_matches = fixtures_service.get_live_fixtures()
            >>> print(f"Live matches: {len(live_matches)}")
        """
        live_param = "all" if league_ids is None else league_ids
        result = self.get_fixtures(live=live_param, timezone=timezone, timeout=timeout)
        return result.get('response', [])
    
    def get_fixtures_by_date(self, match_date: Union[str, date],
                           timezone: Optional[str] = None,
                           timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir tarihteki maçları alır.
        
        Args:
            match_date (Union[str, date]): Maç tarihi (YYYY-MM-DD formatında)
            timezone (Optional[str]): Zaman dilimi
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Maç listesi
            
        Usage:
            >>> fixtures_service = FixturesService()
            >>> matches = fixtures_service.get_fixtures_by_date("2023-12-25")
            >>> print(f"Matches on Christmas: {len(matches)}")
        """
        result = self.get_fixtures(date=match_date, timezone=timezone, timeout=timeout)
        return result.get('response', [])
    
    def get_fixtures_by_league(self, league_id: int, season: int,
                              timezone: Optional[str] = None,
                              timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir lig ve sezondaki maçları alır.
        
        Args:
            league_id (int): Lig ID'si
            season (int): Sezon (YYYY formatında)
            timezone (Optional[str]): Zaman dilimi
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Maç listesi
            
        Usage:
            >>> fixtures_service = FixturesService()
            >>> matches = fixtures_service.get_fixtures_by_league(39, 2023)
            >>> print(f"Premier League 2023 matches: {len(matches)}")
        """
        result = self.get_fixtures(league=league_id, season=season, 
                                 timezone=timezone, timeout=timeout)
        return result.get('response', [])
    
    def get_fixtures_by_team(self, team_id: int, season: Optional[int] = None,
                           last: Optional[int] = None, next: Optional[int] = None,
                           timezone: Optional[str] = None,
                           timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Belirli bir takımın maçlarını alır.
        
        Args:
            team_id (int): Takım ID'si
            season (Optional[int]): Sezon (YYYY formatında)
            last (Optional[int]): Son X maç
            next (Optional[int]): Sonraki X maç
            timezone (Optional[str]): Zaman dilimi
            timeout (Optional[int]): Request timeout süresi (saniye)
            
        Returns:
            List[Dict[str, Any]]: Maç listesi
            
        Usage:
            >>> fixtures_service = FixturesService()
            >>> matches = fixtures_service.get_fixtures_by_team(33, last=5)
            >>> print(f"Manchester United last 5 matches: {len(matches)}")
        """
        result = self.get_fixtures(team=team_id, season=season, last=last, 
                                 next=next, timezone=timezone, timeout=timeout)
        return result.get('response', [])


if __name__ == "__main__":
    # Test fixtures service
    print("Testing Fixtures Service...")
    
    try:
        with FixturesService() as service:
            # Test get fixtures by date
            today_matches = service.get_fixtures_by_date("2023-12-25")
            print(f"✓ Matches on 2023-12-25: {len(today_matches)}")
            
            # Test get live fixtures
            live_matches = service.get_live_fixtures()
            print(f"✓ Live matches: {len(live_matches)}")
            
            # Test get fixtures by league
            league_matches = service.get_fixtures_by_league(39, 2023)
            print(f"✓ Premier League 2023 matches: {len(league_matches)}")
            
            # Test get fixtures by team
            team_matches = service.get_fixtures_by_team(33, last=5)
            print(f"✓ Manchester United last 5 matches: {len(team_matches)}")
            
    except Exception as e:
        print(f"✗ Error testing fixtures service: {e}")
