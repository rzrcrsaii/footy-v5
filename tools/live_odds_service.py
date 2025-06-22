"""
API Football Live Odds Service

Bu modül API Football live odds endpoint'i için servis sınıfını içerir.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional, Union
from .base_service import BaseService
from .api_config import APIConfig


class LiveOddsService(BaseService):
    """
    API Football Live Odds servisi.
    
    Bu servis live odds endpoint'i için kullanılır.
    """
    
    def __init__(self):
        """LiveOddsService sınıfını başlatır."""
        super().__init__()
        self.endpoint = "odds/live"
    
    async def fetch(self, **params) -> Dict[str, Any]:
        """
        Live odds verilerini getirir.

        Args:
            **params: API parametreleri
                - fixture: Fixture ID
                - league: League ID
                - season: Season year
                - bet: Bet ID
                - bookmaker: Bookmaker ID

        Returns:
            Dict[str, Any]: API yanıtı
        """
        return self.get(self.endpoint, params=params)
    
    async def get_by_fixture(self, fixture_id: int, **params) -> Dict[str, Any]:
        """
        Belirli bir fixture için live odds getirir.
        
        Args:
            fixture_id (int): Fixture ID
            **params: Ek parametreler
        
        Returns:
            Dict[str, Any]: API yanıtı
        """
        params['fixture'] = fixture_id
        return await self.fetch(**params)
    
    async def get_by_league(self, league_id: int, season: int, **params) -> Dict[str, Any]:
        """
        Belirli bir lig için live odds getirir.
        
        Args:
            league_id (int): League ID
            season (int): Season year
            **params: Ek parametreler
        
        Returns:
            Dict[str, Any]: API yanıtı
        """
        params.update({
            'league': league_id,
            'season': season
        })
        return await self.fetch(**params)


# Test fonksiyonu
async def test_live_odds_service():
    """LiveOddsService test fonksiyonu."""
    service = LiveOddsService()
    
    try:
        # Test: Fixture bazlı live odds
        print("Testing live odds by fixture...")
        result = await service.get_by_fixture(fixture_id=868847)
        print(f"✅ Live odds by fixture: {len(result.get('response', []))} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Live odds service test failed: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_live_odds_service())
