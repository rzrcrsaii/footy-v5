"""
Footy-Brain v5 Plugins Router
REST API endpoints for wrapper metadata, loading, and management.
"""

from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from apps.api_server.deps import get_optional_user, require_roles, api_rate_limit
from apps.api_server.plugin_loader import (
    plugin_loader, 
    health_check_plugins,
    load_plugin_metadata
)

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class PluginResponse(BaseModel):
    """Plugin response model."""
    
    name: str
    module_name: str
    class_name: str
    endpoint: Optional[str]
    description: Optional[str]
    version: Optional[str]
    is_healthy: bool
    last_check: Optional[str]
    error_message: Optional[str]


class PluginHealthResponse(BaseModel):
    """Plugin health check response."""
    
    plugin_name: str
    is_healthy: bool
    error_message: Optional[str]
    check_time: str


# =============================================================================
# API ENDPOINTS
# =============================================================================

@router.get("/", response_model=List[PluginResponse])
async def get_plugins(
    user: Optional[Dict] = Depends(get_optional_user),
    rate_limit: None = Depends(api_rate_limit)
):
    """Get all discovered plugins with metadata."""
    try:
        metadata = load_plugin_metadata()
        
        plugins = []
        for plugin_data in metadata:
            plugins.append(PluginResponse(**plugin_data))
        
        return plugins
        
    except Exception as e:
        logger.error(f"Error fetching plugins: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{plugin_name}")
async def get_plugin(
    plugin_name: str,
    user: Optional[Dict] = Depends(get_optional_user),
    rate_limit: None = Depends(api_rate_limit)
):
    """Get specific plugin information."""
    try:
        plugin_info = await plugin_loader.get_plugin(plugin_name)
        
        if not plugin_info:
            raise HTTPException(status_code=404, detail="Plugin not found")
        
        return PluginResponse(**plugin_info.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching plugin {plugin_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{plugin_name}/health-check")
async def check_plugin_health(
    plugin_name: str,
    user: Dict = Depends(require_roles(["admin"])),
    rate_limit: None = Depends(api_rate_limit)
):
    """Perform health check on a specific plugin."""
    try:
        is_healthy = await plugin_loader.health_check_plugin(plugin_name)
        plugin_info = await plugin_loader.get_plugin(plugin_name)
        
        if not plugin_info:
            raise HTTPException(status_code=404, detail="Plugin not found")
        
        return PluginHealthResponse(
            plugin_name=plugin_name,
            is_healthy=is_healthy,
            error_message=plugin_info.error_message,
            check_time=plugin_info.last_check.isoformat() if plugin_info.last_check else ""
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking plugin health {plugin_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/health-check-all")
async def check_all_plugins_health(
    user: Dict = Depends(require_roles(["admin"])),
    rate_limit: None = Depends(api_rate_limit)
):
    """Perform health check on all plugins."""
    try:
        health_results = await health_check_plugins()
        
        results = []
        for plugin_name, is_healthy in health_results.items():
            plugin_info = await plugin_loader.get_plugin(plugin_name)
            
            results.append(PluginHealthResponse(
                plugin_name=plugin_name,
                is_healthy=is_healthy,
                error_message=plugin_info.error_message if plugin_info else None,
                check_time=plugin_info.last_check.isoformat() if plugin_info and plugin_info.last_check else ""
            ))
        
        return {
            "total_plugins": len(results),
            "healthy_plugins": sum(1 for r in results if r.is_healthy),
            "unhealthy_plugins": sum(1 for r in results if not r.is_healthy),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error checking all plugins health: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/reload")
async def reload_plugins(
    user: Dict = Depends(require_roles(["admin"])),
    rate_limit: None = Depends(api_rate_limit)
):
    """Reload all plugins (useful for development)."""
    try:
        plugins = await plugin_loader.reload_plugins()
        
        return {
            "status": "reloaded",
            "plugin_count": len(plugins),
            "plugins": [name for name in plugins.keys()]
        }
        
    except Exception as e:
        logger.error(f"Error reloading plugins: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/template/code")
async def get_template_code(
    user: Optional[Dict] = Depends(get_optional_user),
    rate_limit: None = Depends(api_rate_limit)
):
    """Get template wrapper code for creating new plugins."""
    try:
        # Read template_wrapper.py content
        from pathlib import Path
        template_path = Path(__file__).parent.parent.parent.parent / "tools" / "template_wrapper.py"
        
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template_code = f.read()
            
            return {
                "filename": "template_wrapper.py",
                "content": template_code,
                "description": "Template for creating new API wrapper plugins"
            }
        else:
            raise HTTPException(status_code=404, detail="Template file not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching template code: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
