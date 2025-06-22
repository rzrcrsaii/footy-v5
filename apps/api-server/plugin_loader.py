"""
Footy-Brain v5 Plugin Loader
Auto-discovery and loading of API wrapper plugins from /tools directory.
"""

import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Type
import logging

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.base_service import BaseService

logger = logging.getLogger(__name__)


class PluginInfo:
    """Information about a discovered plugin."""
    
    def __init__(
        self,
        name: str,
        module_name: str,
        class_name: str,
        service_class: Type[BaseService],
        endpoint: Optional[str] = None,
        description: Optional[str] = None,
        version: Optional[str] = None
    ):
        self.name = name
        self.module_name = module_name
        self.class_name = class_name
        self.service_class = service_class
        self.endpoint = endpoint
        self.description = description
        self.version = version
        self.is_healthy = False
        self.last_check = None
        self.error_message = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plugin info to dictionary."""
        return {
            "name": self.name,
            "module_name": self.module_name,
            "class_name": self.class_name,
            "endpoint": self.endpoint,
            "description": self.description,
            "version": self.version,
            "is_healthy": self.is_healthy,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "error_message": self.error_message
        }


class PluginLoader:
    """Plugin discovery and loading system."""
    
    def __init__(self, tools_directory: Optional[Path] = None):
        self.tools_directory = tools_directory or (project_root / "tools")
        self.plugins: Dict[str, PluginInfo] = {}
        
    async def discover_plugins(self) -> Dict[str, PluginInfo]:
        """
        Discover all API wrapper plugins in the tools directory.
        
        Returns:
            Dictionary of plugin name to PluginInfo
        """
        logger.info(f"Discovering plugins in {self.tools_directory}")
        
        if not self.tools_directory.exists():
            logger.warning(f"Tools directory not found: {self.tools_directory}")
            return {}
        
        plugins = {}
        
        # Scan for *_service.py files
        for file_path in self.tools_directory.glob("*_service.py"):
            if file_path.name == "base_service.py":
                continue  # Skip base service
                
            try:
                plugin_info = await self._load_plugin_from_file(file_path)
                if plugin_info:
                    plugins[plugin_info.name] = plugin_info
                    logger.info(f"Discovered plugin: {plugin_info.name}")
                    
            except Exception as e:
                logger.error(f"Failed to load plugin from {file_path}: {e}")
        
        self.plugins = plugins
        logger.info(f"Discovered {len(plugins)} plugins total")
        
        return plugins
    
    async def _load_plugin_from_file(self, file_path: Path) -> Optional[PluginInfo]:
        """Load a plugin from a Python file."""
        module_name = f"tools.{file_path.stem}"
        
        try:
            # Import the module
            module = importlib.import_module(module_name)
            
            # Find service classes that inherit from BaseService
            service_classes = []
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (obj != BaseService and 
                    issubclass(obj, BaseService) and 
                    obj.__module__ == module_name):
                    service_classes.append((name, obj))
            
            if not service_classes:
                logger.warning(f"No service classes found in {file_path}")
                return None
            
            # Use the first service class found
            class_name, service_class = service_classes[0]
            
            # Extract metadata from the class
            plugin_name = self._extract_plugin_name(file_path.stem, class_name)
            endpoint = getattr(service_class, 'endpoint', None)
            description = self._extract_description(service_class)
            version = getattr(service_class, 'version', '1.0.0')
            
            plugin_info = PluginInfo(
                name=plugin_name,
                module_name=module_name,
                class_name=class_name,
                service_class=service_class,
                endpoint=endpoint,
                description=description,
                version=version
            )
            
            return plugin_info
            
        except ImportError as e:
            logger.error(f"Failed to import module {module_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading plugin from {file_path}: {e}")
            return None
    
    def _extract_plugin_name(self, file_stem: str, class_name: str) -> str:
        """Extract a friendly plugin name."""
        # Remove _service suffix from file name
        name = file_stem.replace('_service', '')
        
        # Convert snake_case to Title Case
        name = name.replace('_', ' ').title()
        
        return name
    
    def _extract_description(self, service_class: Type[BaseService]) -> str:
        """Extract description from class docstring."""
        docstring = service_class.__doc__
        if not docstring:
            return "No description available"
        
        # Get first line of docstring
        lines = docstring.strip().split('\n')
        return lines[0].strip() if lines else "No description available"
    
    async def get_plugin(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get plugin info by name."""
        return self.plugins.get(plugin_name)
    
    async def create_plugin_instance(self, plugin_name: str) -> Optional[BaseService]:
        """Create an instance of a plugin service."""
        plugin_info = await self.get_plugin(plugin_name)
        if not plugin_info:
            return None
        
        try:
            # Create instance with default configuration
            instance = plugin_info.service_class()
            return instance
        except Exception as e:
            logger.error(f"Failed to create instance of {plugin_name}: {e}")
            return None
    
    async def health_check_plugin(self, plugin_name: str) -> bool:
        """
        Perform health check on a plugin by making a test API call.
        
        Args:
            plugin_name: Name of the plugin to check
            
        Returns:
            True if plugin is healthy, False otherwise
        """
        plugin_info = await self.get_plugin(plugin_name)
        if not plugin_info:
            return False
        
        try:
            # Create plugin instance
            instance = await self.create_plugin_instance(plugin_name)
            if not instance:
                return False
            
            # Try to make a simple API call
            # This is a basic health check - plugins can override this
            if hasattr(instance, 'health_check'):
                result = await instance.health_check()
                plugin_info.is_healthy = result
                plugin_info.error_message = None
            else:
                # Default health check - try to fetch with minimal parameters
                try:
                    await instance.fetch()
                    plugin_info.is_healthy = True
                    plugin_info.error_message = None
                except Exception as e:
                    plugin_info.is_healthy = False
                    plugin_info.error_message = str(e)
            
            plugin_info.last_check = datetime.utcnow()
            return plugin_info.is_healthy
            
        except Exception as e:
            logger.error(f"Health check failed for {plugin_name}: {e}")
            plugin_info.is_healthy = False
            plugin_info.error_message = str(e)
            plugin_info.last_check = datetime.utcnow()
            return False
    
    async def health_check_all_plugins(self) -> Dict[str, bool]:
        """Perform health check on all plugins."""
        results = {}
        
        for plugin_name in self.plugins.keys():
            results[plugin_name] = await self.health_check_plugin(plugin_name)
        
        return results
    
    def get_plugin_metadata(self) -> List[Dict[str, Any]]:
        """Get metadata for all discovered plugins."""
        return [plugin.to_dict() for plugin in self.plugins.values()]
    
    async def reload_plugins(self) -> Dict[str, PluginInfo]:
        """Reload all plugins (useful for development)."""
        logger.info("Reloading plugins...")
        
        # Clear existing plugins
        self.plugins.clear()
        
        # Reload modules
        for module_name in list(sys.modules.keys()):
            if module_name.startswith('tools.') and module_name.endswith('_service'):
                try:
                    importlib.reload(sys.modules[module_name])
                except Exception as e:
                    logger.error(f"Failed to reload module {module_name}: {e}")
        
        # Rediscover plugins
        return await self.discover_plugins()


# Global plugin loader instance
plugin_loader = PluginLoader()


async def discover_plugins() -> Dict[str, PluginInfo]:
    """Convenience function to discover plugins."""
    return await plugin_loader.discover_plugins()


async def get_plugin_instance(plugin_name: str) -> Optional[BaseService]:
    """Convenience function to get plugin instance."""
    return await plugin_loader.create_plugin_instance(plugin_name)


async def health_check_plugins() -> Dict[str, bool]:
    """Convenience function to health check all plugins."""
    return await plugin_loader.health_check_all_plugins()


def load_plugin_metadata() -> List[Dict[str, Any]]:
    """Convenience function to get plugin metadata."""
    return plugin_loader.get_plugin_metadata()


# Import datetime for health check timestamps
from datetime import datetime
