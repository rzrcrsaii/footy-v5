"""
API Football Configuration Module

Bu modül API Football servisine erişim için gerekli konfigürasyon ayarlarını içerir.
API anahtarı ve base URL gibi temel ayarlar burada tanımlanmıştır.

Author: API Football Python Wrapper
Version: 1.0.0
"""

import os
from typing import Dict, Optional

# API Football Base Configuration
API_BASE_URL = "https://v3.football.api-sports.io"
API_HOST = "v3.football.api-sports.io"

# API Key - Fixed key for development
RAPIDAPI_KEY = "65ded8ae3bf506066acc2e2343b6eec9"
API_KEY = os.getenv('RAPIDAPI_KEY', RAPIDAPI_KEY)

# Request Headers Template
DEFAULT_HEADERS = {
    'X-RapidAPI-Host': API_HOST,
    'X-RapidAPI-Key': API_KEY,
    'Content-Type': 'application/json'
}

# Timeout Settings (seconds)
REQUEST_TIMEOUT = 30
CONNECTION_TIMEOUT = 10

# Rate Limiting Settings (RapidAPI limits)
RATE_LIMIT_PER_MINUTE = 100
RATE_LIMIT_PER_DAY = 1000
RATE_LIMIT_PER_SECOND = 6  # 6 requests per second max

# Retry Settings
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Cache Settings
CACHE_ENABLED = True
CACHE_TTL = 3600  # 1 hour in seconds

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class APIConfig:
    """
    API Football konfigürasyon sınıfı.
    
    Bu sınıf API ile ilgili tüm konfigürasyon ayarlarını yönetir.
    Environment variable'lar üzerinden konfigürasyon değişikliği yapılabilir.
    """
    
    def __init__(self):
        self.api_key = self._get_api_key()
        self.base_url = self._get_base_url()
        self.headers = self._build_headers()
        self.timeout = self._get_timeout()
        
    def _get_api_key(self) -> str:
        """
        API anahtarını environment variable'dan alır.

        Returns:
            str: API anahtarı

        Raises:
            ValueError: API anahtarı bulunamazsa
        """
        api_key = os.getenv('RAPIDAPI_KEY', API_KEY)
        if not api_key or api_key == 'your_rapidapi_key_here':
            # Use the fixed development key
            api_key = RAPIDAPI_KEY
        return api_key
    
    def _get_base_url(self) -> str:
        """
        Base URL'i environment variable'dan veya default değerden alır.
        
        Returns:
            str: Base URL
        """
        return os.getenv('API_FOOTBALL_BASE_URL', API_BASE_URL)
    
    def _build_headers(self) -> Dict[str, str]:
        """
        HTTP request header'larını oluşturur.

        Returns:
            Dict[str, str]: Request headers
        """
        return {
            'X-RapidAPI-Host': API_HOST,
            'X-RapidAPI-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def _get_timeout(self) -> int:
        """
        Request timeout değerini alır.
        
        Returns:
            int: Timeout değeri (saniye)
        """
        return int(os.getenv('API_FOOTBALL_TIMEOUT', REQUEST_TIMEOUT))
    
    def update_api_key(self, new_api_key: str) -> None:
        """
        API anahtarını günceller.
        
        Args:
            new_api_key (str): Yeni API anahtarı
        """
        self.api_key = new_api_key
        self.headers = self._build_headers()
    
    def get_endpoint_url(self, endpoint: str) -> str:
        """
        Verilen endpoint için tam URL oluşturur.
        
        Args:
            endpoint (str): API endpoint (örn: '/leagues')
            
        Returns:
            str: Tam URL
        """
        if endpoint.startswith('/'):
            return f"{self.base_url}{endpoint}"
        return f"{self.base_url}/{endpoint}"


# Global config instance
config = APIConfig()


def get_config() -> APIConfig:
    """
    Global konfigürasyon instance'ını döndürür.
    
    Returns:
        APIConfig: Konfigürasyon instance'ı
    """
    return config


def set_api_key(api_key: str) -> None:
    """
    Global API anahtarını günceller.
    
    Args:
        api_key (str): Yeni API anahtarı
    """
    global config
    config.update_api_key(api_key)


# Environment variable kontrolü
if __name__ == "__main__":
    print(f"API Base URL: {config.base_url}")
    print(f"API Key: {'*' * (len(config.api_key) - 4) + config.api_key[-4:]}")
    print(f"Headers: {config.headers}")
