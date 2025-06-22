"""
API Football Live Stats Service

Bu modül API Football fixture statistics endpoint'i için servis sınıfını içerir.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional, Union
from .base_service import BaseService
from .api_config import APIConfig


class LiveStatsService(BaseService):
    """
    API Football Live Stats servisi.
    
    Bu servis fixture statistics endpoint'i için kullanılır.
    """
    
    def __init__(self):
        """LiveStatsService sınıfını başlatır."""
        super().__init__()
        self.endpoint = "fixtures/statistics"
    
    async def fetch(self, **params) -> Dict[str, Any]:
        """
        Live statistics verilerini getirir.

        Args:
            **params: API parametreleri
                - fixture: Fixture ID
                - team: Team ID

        Returns:
            Dict[str, Any]: API yanıtı
        """
        return self.get(self.endpoint, params=params)
    
    async def get_by_fixture(self, fixture_id: int, **params) -> Dict[str, Any]:
        """
        Belirli bir fixture için statistics getirir.
        
        Args:
            fixture_id (int): Fixture ID
            **params: Ek parametreler
        
        Returns:
            Dict[str, Any]: API yanıtı
        """
        params['fixture'] = fixture_id
        return await self.fetch(**params)
    
    async def get_by_team(self, team_id: int, fixture_id: int, **params) -> Dict[str, Any]:
        """
        Belirli bir takım için statistics getirir.
        
        Args:
            team_id (int): Team ID
            fixture_id (int): Fixture ID
            **params: Ek parametreler
        
        Returns:
            Dict[str, Any]: API yanıtı
        """
        params.update({
            'team': team_id,
            'fixture': fixture_id
        })
        return await self.fetch(**params)


# Test fonksiyonu
async def test_live_stats_service():
    """LiveStatsService test fonksiyonu."""
    service = LiveStatsService()
    
    try:
        # Test: Fixture bazlı statistics
        print("Testing live stats by fixture...")
        result = await service.get_by_fixture(fixture_id=868847)
        print(f"✅ Live stats by fixture: {len(result.get('response', []))} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Live stats service test failed: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_live_stats_service())
