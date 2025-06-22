"""
API Football Base Service Module

Bu modül tüm API Football servislerinin temel sınıfını içerir.
HTTP request handling, response parsing ve error handling için
ortak fonksiyonalite sağlar.

Author: API Football Python Wrapper
Version: 1.0.0
"""

import requests
import json
import time
from typing import Dict, Any, Optional, Union, List
from urllib.parse import urlencode

from .api_config import get_config, APIConfig
from .error_handler import handle_api_response, ErrorHandler


class BaseService:
    """
    API Football servisleri için temel sınıf.
    
    Bu sınıf HTTP request handling, response parsing, error handling
    ve rate limiting gibi ortak fonksiyonaliteleri sağlar.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        BaseAPIService constructor.
        
        Args:
            config (Optional[APIConfig]): API konfigürasyonu. None ise default config kullanılır.
        """
        self.config = config or get_config()
        self.error_handler = ErrorHandler()
        self.session = requests.Session()
        self.session.headers.update(self.config.headers)
        
        # Rate limiting için (RapidAPI: max 6 requests per second)
        self._last_request_time = 0
        self._min_request_interval = 1.0 / 6.0  # 6 requests per second = ~0.167 seconds between requests
    
    def _wait_for_rate_limit(self) -> None:
        """
        Rate limiting için gerekli bekleme süresini uygular.
        """
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        
        if time_since_last_request < self._min_request_interval:
            sleep_time = self._min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def _build_url(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        API endpoint URL'ini oluşturur.
        
        Args:
            endpoint (str): API endpoint
            params (Optional[Dict[str, Any]]): Query parametreleri
            
        Returns:
            str: Tam URL
        """
        base_url = self.config.get_endpoint_url(endpoint)
        
        if params:
            # None değerleri filtrele
            filtered_params = {k: v for k, v in params.items() if v is not None}
            if filtered_params:
                query_string = urlencode(filtered_params)
                return f"{base_url}?{query_string}"
        
        return base_url
    
    def _make_request(self, method: str, endpoint: str, 
                     params: Optional[Dict[str, Any]] = None,
                     data: Optional[Dict[str, Any]] = None,
                     timeout: Optional[int] = None) -> requests.Response:
        """
        HTTP request yapar.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint
            params (Optional[Dict[str, Any]]): Query parametreleri
            data (Optional[Dict[str, Any]]): Request body data
            timeout (Optional[int]): Request timeout
            
        Returns:
            requests.Response: HTTP response
            
        Raises:
            requests.RequestException: Request hatası durumunda
        """
        # Rate limiting uygula
        self._wait_for_rate_limit()
        
        # URL oluştur
        url = self._build_url(endpoint, params)
        
        # Request logla
        self.error_handler.log_request(endpoint, params)
        
        # Timeout ayarla
        request_timeout = timeout or self.config.timeout
        
        try:
            # Request yap
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=request_timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=request_timeout)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, timeout=request_timeout)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=request_timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Response logla
            self.error_handler.log_response(response.status_code, len(response.content))
            
            return response
            
        except requests.Timeout:
            raise requests.RequestException(f"Request timeout after {request_timeout} seconds")
        except requests.ConnectionError:
            raise requests.RequestException("Connection error - Unable to connect to API")
        except requests.RequestException as e:
            raise requests.RequestException(f"Request failed: {str(e)}")
    
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        HTTP response'u parse eder ve hata kontrolü yapar.
        
        Args:
            response (requests.Response): HTTP response
            
        Returns:
            Dict[str, Any]: Parse edilmiş response data
            
        Raises:
            APIFootballException: API hatası durumunda
        """
        try:
            # JSON parse et
            if response.content:
                response_data = response.json()
            else:
                response_data = {}
            
            # Response yapısını doğrula
            if response.status_code == 200 and response_data:
                if not self.error_handler.validate_response_structure(response_data):
                    # Yapı geçersiz ama 200 OK, warning ver ve devam et
                    pass
            
            # Status koduna göre işle
            result = handle_api_response(response.status_code, response_data)
            return result or response_data
            
        except json.JSONDecodeError:
            # JSON parse hatası
            error_msg = f"Invalid JSON response: {response.text[:200]}"
            handle_api_response(response.status_code, {"message": error_msg})
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
            timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        GET request yapar.
        
        Args:
            endpoint (str): API endpoint
            params (Optional[Dict[str, Any]]): Query parametreleri
            timeout (Optional[int]): Request timeout
            
        Returns:
            Dict[str, Any]: API response data
        """
        response = self._make_request('GET', endpoint, params=params, timeout=timeout)
        return self._parse_response(response)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
             params: Optional[Dict[str, Any]] = None, 
             timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        POST request yapar.
        
        Args:
            endpoint (str): API endpoint
            data (Optional[Dict[str, Any]]): Request body data
            params (Optional[Dict[str, Any]]): Query parametreleri
            timeout (Optional[int]): Request timeout
            
        Returns:
            Dict[str, Any]: API response data
        """
        response = self._make_request('POST', endpoint, params=params, data=data, timeout=timeout)
        return self._parse_response(response)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
            params: Optional[Dict[str, Any]] = None, 
            timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        PUT request yapar.
        
        Args:
            endpoint (str): API endpoint
            data (Optional[Dict[str, Any]]): Request body data
            params (Optional[Dict[str, Any]]): Query parametreleri
            timeout (Optional[int]): Request timeout
            
        Returns:
            Dict[str, Any]: API response data
        """
        response = self._make_request('PUT', endpoint, params=params, data=data, timeout=timeout)
        return self._parse_response(response)
    
    def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
               timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        DELETE request yapar.
        
        Args:
            endpoint (str): API endpoint
            params (Optional[Dict[str, Any]]): Query parametreleri
            timeout (Optional[int]): Request timeout
            
        Returns:
            Dict[str, Any]: API response data
        """
        response = self._make_request('DELETE', endpoint, params=params, timeout=timeout)
        return self._parse_response(response)

    def fetch(self, **params) -> dict:
        """
        Generic fetch method that all services must implement.
        This is the standard interface for system prompt compatibility.

        Args:
            **params: Endpoint-specific parameters

        Returns:
            dict: API response data

        Note:
            This is a base implementation. Subclasses should override this
            method to provide endpoint-specific functionality.
        """
        # Default implementation uses GET with the service's endpoint
        if hasattr(self, 'endpoint'):
            return self.get(self.endpoint, params=params)
        else:
            raise NotImplementedError("Subclass must implement fetch() method or set self.endpoint")

    def close(self) -> None:
        """
        HTTP session'ı kapatır.
        """
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == "__main__":
    # Test base service
    with BaseService() as service:
        try:
            # Test timezone endpoint
            result = service.get('/timezone')
            print(f"✓ Base service test successful. Results: {result.get('results', 0)}")
        except Exception as e:
            print(f"✗ Base service test failed: {e}")
