"""
Footy-Brain v5 API Routers
FastAPI router modules for different API endpoints.
"""

# Import all routers for easy access
from . import fixtures
from . import live
from . import prematch
from . import cronjobs
from . import settings
from . import plugins

__all__ = [
    "fixtures",
    "live", 
    "prematch",
    "cronjobs",
    "settings",
    "plugins"
]
