"""
API Football Template Wrapper Module

Bu modül yeni API Football endpoint'leri için şablon sınıfını içerir.
Yeni servis oluştururken bu dosyayı kopyalayıp düzenleyebilirsiniz.

Author: API Football Python Wrapper
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional, Union
from .base_service import BaseService
from .api_config import APIConfig


class TemplateService(BaseService):
    """
    API Football Template servisi.
    
    Bu servis yeni endpoint'ler için şablon olarak kullanılır.
    Kopyalayıp endpoint'inize göre düzenleyin.
    
    Usage:
        >>> template_service = TemplateService()
        >>> result = template_service.fetch(param1="value1", param2="value2")
        >>> print(f"Results: {result['results']}")
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        TemplateService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu
        """
        super().__init__(config)
        self.endpoint = '/your-endpoint-here'  # TODO: Gerçek endpoint'i buraya yazın
        
    def fetch(self, **params) -> Dict[str, Any]:
        """
        Generic fetch method for the endpoint.
        
        Bu method'u endpoint'inizin parametrelerine göre özelleştirin.
        
        Args:
            **params: Endpoint parametreleri
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Raises:
            APIFootballException: API hatası durumunda
            
        Usage:
            >>> service = TemplateService()
            >>> result = service.fetch(param1="value", param2=123)
        """
        # Parametre validasyonu
        validated_params = self._validate_params(params)
        
        # API çağrısı
        response = self.get(self.endpoint, params=validated_params)
        
        return response
    
    def _validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parametreleri validate eder ve temizler.
        
        Args:
            params (Dict[str, Any]): Ham parametreler
            
        Returns:
            Dict[str, Any]: Validate edilmiş parametreler
            
        Raises:
            ValueError: Geçersiz parametre durumunda
        """
        validated = {}
        
        # TODO: Endpoint'inizin parametrelerine göre validation kuralları ekleyin
        
        # Örnek validasyonlar:
        
        # ID parametresi (zorunlu)
        if 'id' in params:
            if not isinstance(params['id'], (int, str)):
                raise ValueError("ID must be integer or string")
            validated['id'] = params['id']
        
        # Liste parametresi (opsiyonel)
        if 'ids' in params:
            if isinstance(params['ids'], (list, tuple)):
                if len(params['ids']) > 20:  # API limiti
                    raise ValueError("Maximum 20 IDs allowed")
                validated['ids'] = '-'.join(map(str, params['ids']))
            else:
                validated['ids'] = str(params['ids'])
        
        # Tarih parametresi (opsiyonel)
        if 'date' in params:
            date_value = params['date']
            if isinstance(date_value, str):
                # YYYY-MM-DD formatını kontrol et
                try:
                    from datetime import datetime
                    datetime.strptime(date_value, '%Y-%m-%d')
                    validated['date'] = date_value
                except ValueError:
                    raise ValueError("Date must be in YYYY-MM-DD format")
            else:
                raise ValueError("Date must be string in YYYY-MM-DD format")
        
        # Sayısal parametre (opsiyonel)
        if 'season' in params:
            season = params['season']
            if isinstance(season, int):
                if season < 2000 or season > 2030:
                    raise ValueError("Season must be between 2000 and 2030")
                validated['season'] = season
            else:
                raise ValueError("Season must be integer")
        
        # Boolean parametre (opsiyonel)
        if 'live' in params:
            live_value = params['live']
            if isinstance(live_value, bool):
                validated['live'] = 'all' if live_value else None
            elif isinstance(live_value, str):
                validated['live'] = live_value
            else:
                raise ValueError("Live parameter must be boolean or string")
        
        # String parametre (opsiyonel)
        if 'status' in params:
            status = params['status']
            if isinstance(status, str):
                # Geçerli status değerlerini kontrol et
                valid_statuses = ['NS', '1H', 'HT', '2H', 'ET', 'FT', 'AET', 'PEN', 'SUSP', 'INT', 'CANC']
                if status.upper() in valid_statuses:
                    validated['status'] = status.upper()
                else:
                    raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
            else:
                raise ValueError("Status must be string")
        
        # Timeout parametresi (opsiyonel)
        if 'timeout' in params:
            timeout = params['timeout']
            if isinstance(timeout, (int, float)):
                if timeout > 0:
                    validated['timeout'] = timeout
                else:
                    raise ValueError("Timeout must be positive number")
            else:
                raise ValueError("Timeout must be number")
        
        return validated
    
    def get_by_id(self, entity_id: Union[int, str], **kwargs) -> Dict[str, Any]:
        """
        ID ile tek bir entity getirir.
        
        Args:
            entity_id (Union[int, str]): Entity ID
            **kwargs: Ek parametreler
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Usage:
            >>> service = TemplateService()
            >>> result = service.get_by_id(123)
        """
        params = {'id': entity_id}
        params.update(kwargs)
        return self.fetch(**params)
    
    def get_by_ids(self, entity_ids: List[Union[int, str]], **kwargs) -> Dict[str, Any]:
        """
        Birden fazla ID ile entity'leri getirir.
        
        Args:
            entity_ids (List[Union[int, str]]): Entity ID listesi
            **kwargs: Ek parametreler
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Usage:
            >>> service = TemplateService()
            >>> result = service.get_by_ids([123, 456, 789])
        """
        params = {'ids': entity_ids}
        params.update(kwargs)
        return self.fetch(**params)
    
    def get_live(self, **kwargs) -> Dict[str, Any]:
        """
        Canlı verileri getirir (eğer endpoint destekliyorsa).
        
        Args:
            **kwargs: Ek parametreler
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Usage:
            >>> service = TemplateService()
            >>> result = service.get_live()
        """
        params = {'live': True}
        params.update(kwargs)
        return self.fetch(**params)
    
    def get_by_date(self, date: str, **kwargs) -> Dict[str, Any]:
        """
        Belirli bir tarihe ait verileri getirir.
        
        Args:
            date (str): Tarih (YYYY-MM-DD formatında)
            **kwargs: Ek parametreler
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Usage:
            >>> service = TemplateService()
            >>> result = service.get_by_date("2024-01-15")
        """
        params = {'date': date}
        params.update(kwargs)
        return self.fetch(**params)
    
    def get_by_season(self, season: int, **kwargs) -> Dict[str, Any]:
        """
        Belirli bir sezona ait verileri getirir.
        
        Args:
            season (int): Sezon yılı
            **kwargs: Ek parametreler
            
        Returns:
            Dict[str, Any]: API yanıtı
            
        Usage:
            >>> service = TemplateService()
            >>> result = service.get_by_season(2024)
        """
        params = {'season': season}
        params.update(kwargs)
        return self.fetch(**params)


# Yeni servis oluştururken bu adımları takip edin:
"""
1. Bu dosyayı kopyalayın: cp template_wrapper.py your_new_service.py
2. Sınıf adını değiştirin: TemplateService -> YourNewService
3. Endpoint'i güncelleyin: self.endpoint = '/your-actual-endpoint'
4. _validate_params method'unu endpoint'inizin parametrelerine göre düzenleyin
5. Gerekirse özel method'lar ekleyin
6. Docstring'leri güncelleyin
7. Test edin!

Örnek:
class FixturesService(BaseService):
    def __init__(self, config: Optional[APIConfig] = None):
        super().__init__(config)
        self.endpoint = '/fixtures'
    
    def _validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Fixtures endpoint'ine özel validasyonlar
        pass
"""
