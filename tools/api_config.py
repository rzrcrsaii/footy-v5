#!/usr/bin/env python3
"""
API Configuration Module
========================

Centralized configuration for all API services.
Contains API keys, endpoints, and common settings.
"""

import os
from typing import Dict, Any

# RapidAPI Configuration
RAPIDAPI_KEY = "65ded8ae3bf506066acc2e2343b6eec9"
RAPIDAPI_HOST = "api-football-v1.p.rapidapi.com"
RAPIDAPI_BASE_URL = f"https://{RAPIDAPI_HOST}/v3"

# Common headers for all RapidAPI requests
RAPIDAPI_HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": RAPIDAPI_HOST,
    "Content-Type": "application/json"
}

class APIConfig:
    """
    Centralized API configuration class.
    """
    
    # RapidAPI Settings
    RAPIDAPI_KEY = RAPIDAPI_KEY
    RAPIDAPI_HOST = RAPIDAPI_HOST
    RAPIDAPI_BASE_URL = RAPIDAPI_BASE_URL
    RAPIDAPI_HEADERS = RAPIDAPI_HEADERS
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = 100
    RATE_LIMIT_PER_DAY = 1000
    
    # Timeout Settings
    REQUEST_TIMEOUT = 30
    CONNECTION_TIMEOUT = 10
    
    # Retry Settings
    MAX_RETRIES = 3
    RETRY_DELAY = 1
    
    # Cache Settings
    CACHE_TTL = 300  # 5 minutes
    CACHE_ENABLED = True
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_API_REQUESTS = True
    LOG_API_RESPONSES = False  # Set to True for debugging
    
    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        """Get standard headers for API requests."""
        return cls.RAPIDAPI_HEADERS.copy()
    
    @classmethod
    def get_base_url(cls) -> str:
        """Get base URL for API requests."""
        return cls.RAPIDAPI_BASE_URL
    
    @classmethod
    def get_timeout(cls) -> int:
        """Get request timeout."""
        return cls.REQUEST_TIMEOUT
    
    @classmethod
    def is_cache_enabled(cls) -> bool:
        """Check if caching is enabled."""
        return cls.CACHE_ENABLED
    
    @classmethod
    def get_cache_ttl(cls) -> int:
        """Get cache TTL in seconds."""
        return cls.CACHE_TTL

# Environment-based overrides
if os.getenv("RAPIDAPI_KEY"):
    APIConfig.RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
    APIConfig.RAPIDAPI_HEADERS["X-RapidAPI-Key"] = os.getenv("RAPIDAPI_KEY")

if os.getenv("REQUEST_TIMEOUT"):
    APIConfig.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT"))

if os.getenv("CACHE_ENABLED"):
    APIConfig.CACHE_ENABLED = os.getenv("CACHE_ENABLED").lower() == "true"

if os.getenv("LOG_LEVEL"):
    APIConfig.LOG_LEVEL = os.getenv("LOG_LEVEL")

# Export commonly used values
__all__ = [
    "APIConfig",
    "RAPIDAPI_KEY",
    "RAPIDAPI_HOST",
    "RAPIDAPI_BASE_URL",
    "RAPIDAPI_HEADERS"
]