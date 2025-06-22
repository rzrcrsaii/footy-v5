"""
API Football Error Handler Module

Bu modül API Football servisinden gelen HTTP hata kodlarını yönetir.
Standart hata sınıfları ve handling fonksiyonları içerir.

Author: API Football Python Wrapper
Version: 1.0.0
"""

import logging
import json
from typing import Dict, Any, Optional, Union
from datetime import datetime


# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIFootballException(Exception):
    """
    API Football için temel exception sınıfı.
    """
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        self.timestamp = datetime.now()
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return f"APIFootballException: {self.message} (Status: {self.status_code})"


class APISuccessResponse(APIFootballException):
    """
    200 - Başarılı response için sınıf.
    Teknik olarak exception değil ama tutarlılık için bu yapıda.
    """
    
    def __init__(self, message: str = "Request successful", response_data: Optional[Dict] = None):
        super().__init__(message, 200, response_data)


class APINoContentException(APIFootballException):
    """
    204 - İçerik bulunamadı hatası.
    """
    
    def __init__(self, message: str = "No content found for the requested parameters", response_data: Optional[Dict] = None):
        super().__init__(message, 204, response_data)


class APITimeoutException(APIFootballException):
    """
    499 - İstemci bağlantısı kesildi hatası.
    """
    
    def __init__(self, message: str = "Client closed request - Request timeout", response_data: Optional[Dict] = None):
        super().__init__(message, 499, response_data)


class APIServerException(APIFootballException):
    """
    500 - Sunucu hatası.
    """
    
    def __init__(self, message: str = "Internal server error", response_data: Optional[Dict] = None):
        super().__init__(message, 500, response_data)


class APIRateLimitException(APIFootballException):
    """
    429 - Rate limit aşıldı hatası.
    """
    
    def __init__(self, message: str = "Rate limit exceeded", response_data: Optional[Dict] = None):
        super().__init__(message, 429, response_data)


class APIAuthenticationException(APIFootballException):
    """
    401/403 - Authentication/Authorization hatası.
    """
    
    def __init__(self, message: str = "Authentication failed", response_data: Optional[Dict] = None):
        super().__init__(message, 401, response_data)


class ErrorHandler:
    """
    API Football hata yönetimi sınıfı.
    
    HTTP status kodlarına göre uygun exception'ları fırlatır ve
    hata loglaması yapar.
    """
    
    @staticmethod
    def handle_response(status_code: int, response_data: Optional[Dict] = None, 
                       custom_message: Optional[str] = None) -> Union[Dict, None]:
        """
        HTTP response'u status koduna göre işler.
        
        Args:
            status_code (int): HTTP status kodu
            response_data (Optional[Dict]): Response verisi
            custom_message (Optional[str]): Özel hata mesajı
            
        Returns:
            Union[Dict, None]: Başarılı ise response data, hata varsa None
            
        Raises:
            APIFootballException: İlgili hata türüne göre exception
        """
        
        # Response data'dan hata mesajını çıkar
        error_message = custom_message
        if response_data and isinstance(response_data, dict):
            if 'message' in response_data:
                error_message = response_data['message']
            elif 'errors' in response_data and response_data['errors']:
                error_message = str(response_data['errors'])
        
        # Status koduna göre işlem yap
        if status_code == 200:
            logger.info("API request successful")
            return response_data
            
        elif status_code == 204:
            error_msg = error_message or "No content found for the requested parameters"
            logger.warning(f"No content: {error_msg}")
            raise APINoContentException(error_msg, response_data)
            
        elif status_code == 401:
            error_msg = error_message or "Authentication failed - Invalid API key"
            logger.error(f"Authentication error: {error_msg}")
            raise APIAuthenticationException(error_msg, response_data)
            
        elif status_code == 403:
            error_msg = error_message or "Access forbidden - Check API permissions"
            logger.error(f"Authorization error: {error_msg}")
            raise APIAuthenticationException(error_msg, response_data)
            
        elif status_code == 429:
            error_msg = error_message or "Rate limit exceeded - Too many requests"
            logger.error(f"Rate limit error: {error_msg}")
            raise APIRateLimitException(error_msg, response_data)
            
        elif status_code == 499:
            error_msg = error_message or "Client closed request - Request timeout"
            logger.error(f"Timeout error: {error_msg}")
            raise APITimeoutException(error_msg, response_data)
            
        elif status_code == 500:
            error_msg = error_message or "Internal server error"
            logger.error(f"Server error: {error_msg}")
            raise APIServerException(error_msg, response_data)
            
        else:
            error_msg = error_message or f"Unexpected HTTP status code: {status_code}"
            logger.error(f"Unknown error: {error_msg}")
            raise APIFootballException(error_msg, status_code, response_data)
    
    @staticmethod
    def log_request(endpoint: str, params: Optional[Dict] = None) -> None:
        """
        API request'i loglar.
        
        Args:
            endpoint (str): API endpoint
            params (Optional[Dict]): Request parametreleri
        """
        logger.info(f"API Request - Endpoint: {endpoint}, Params: {params}")
    
    @staticmethod
    def log_response(status_code: int, response_size: int = 0) -> None:
        """
        API response'u loglar.
        
        Args:
            status_code (int): HTTP status kodu
            response_size (int): Response boyutu
        """
        logger.info(f"API Response - Status: {status_code}, Size: {response_size} bytes")
    
    @staticmethod
    def validate_response_structure(response_data: Dict) -> bool:
        """
        API response yapısını doğrular.
        
        Args:
            response_data (Dict): Response verisi
            
        Returns:
            bool: Yapı geçerli ise True
        """
        required_fields = ['get', 'parameters', 'errors', 'results', 'response']
        
        if not isinstance(response_data, dict):
            logger.error("Response is not a dictionary")
            return False
        
        for field in required_fields:
            if field not in response_data:
                logger.error(f"Missing required field in response: {field}")
                return False
        
        return True
    
    @staticmethod
    def extract_error_details(response_data: Dict) -> Optional[str]:
        """
        Response'dan hata detaylarını çıkarır.
        
        Args:
            response_data (Dict): Response verisi
            
        Returns:
            Optional[str]: Hata detayları
        """
        if not response_data:
            return None
        
        # Errors array'ini kontrol et
        if 'errors' in response_data and response_data['errors']:
            errors = response_data['errors']
            if isinstance(errors, list) and errors:
                return str(errors[0])
            elif isinstance(errors, dict):
                return errors.get('report', str(errors))
        
        # Message field'ını kontrol et
        if 'message' in response_data:
            return response_data['message']
        
        return None


# Global error handler instance
error_handler = ErrorHandler()


def handle_api_response(status_code: int, response_data: Optional[Dict] = None, 
                       custom_message: Optional[str] = None) -> Union[Dict, None]:
    """
    API response'u işlemek için global fonksiyon.
    
    Args:
        status_code (int): HTTP status kodu
        response_data (Optional[Dict]): Response verisi
        custom_message (Optional[str]): Özel hata mesajı
        
    Returns:
        Union[Dict, None]: İşlenmiş response
    """
    return error_handler.handle_response(status_code, response_data, custom_message)


if __name__ == "__main__":
    # Test cases
    print("Error Handler Test Cases:")
    
    # Test successful response
    try:
        result = handle_api_response(200, {"data": "test"})
        print("✓ 200 OK handled successfully")
    except Exception as e:
        print(f"✗ 200 OK test failed: {e}")
    
    # Test no content
    try:
        handle_api_response(204)
        print("✗ 204 should raise exception")
    except APINoContentException:
        print("✓ 204 No Content handled successfully")
    
    # Test server error
    try:
        handle_api_response(500)
        print("✗ 500 should raise exception")
    except APIServerException:
        print("✓ 500 Server Error handled successfully")
