"""
API Football Live Events Service

Bu modül API Football fixture events endpoint'i için servis sınıfını içerir.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional, Union
from .base_service import BaseService
from .api_config import APIConfig


class LiveEventsService(BaseService):
    """
    API Football Live Events servisi.
    
    Bu servis fixture events endpoint'i için kullanılır.
    """
    
    def __init__(self):
        """LiveEventsService sınıfını başlatır."""
        super().__init__()
        self.endpoint = "fixtures/events"
    
    async def fetch(self, **params) -> Dict[str, Any]:
        """
        Live events verilerini getirir.

        Args:
            **params: API parametreleri
                - fixture: Fixture ID
                - team: Team ID
                - player: Player ID
                - type: Event type

        Returns:
            Dict[str, Any]: API yanıtı
        """
        return self.get(self.endpoint, params=params)
    
    async def get_by_fixture(self, fixture_id: int, **params) -> Dict[str, Any]:
        """
        Belirli bir fixture için events getirir.
        
        Args:
            fixture_id (int): Fixture ID
            **params: Ek parametreler
        
        Returns:
            Dict[str, Any]: API yanıtı
        """
        params['fixture'] = fixture_id
        return await self.fetch(**params)
    
    async def get_by_team(self, team_id: int, **params) -> Dict[str, Any]:
        """
        Belirli bir takım için events getirir.
        
        Args:
            team_id (int): Team ID
            **params: Ek parametreler
        
        Returns:
            Dict[str, Any]: API yanıtı
        """
        params['team'] = team_id
        return await self.fetch(**params)


# Test fonksiyonu
async def test_live_events_service():
    """LiveEventsService test fonksiyonu."""
    service = LiveEventsService()
    
    try:
        # Test: Fixture bazlı events
        print("Testing live events by fixture...")
        result = await service.get_by_fixture(fixture_id=868847)
        print(f"✅ Live events by fixture: {len(result.get('response', []))} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Live events service test failed: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_live_events_service())
