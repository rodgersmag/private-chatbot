"""CORS origins loader for dynamic CORS management."""

import asyncio
from typing import List, Set
import logging
from datetime import datetime, timedelta

from ..core.config import settings
from ..services.cors_service import CorsService
from ..db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


class CorsOriginsLoader:
    """Manages dynamic loading and caching of CORS origins."""
    
    def __init__(self):
        self._cached_origins: Set[str] = set()
        self._last_refresh: datetime = datetime.min
        self._cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
        self._is_refreshing = False
    
    async def get_all_origins(self) -> List[str]:
        """
        Get all CORS origins combining environment variables and database origins.
        
        Returns:
            List of origin URLs
        """
        # Always include environment variable origins
        env_origins = set(settings.cors_origins_list)
        
        # Always include default origins
        default_origins = {
            "http://localhost",
            "http://localhost:3000",
            "http://frontend:3000",
        }
        
        # Get database origins (with caching)
        db_origins = await self._get_database_origins()
        
        # Combine all origins
        all_origins = env_origins | default_origins | db_origins
        
        # Convert to list and log for debugging
        origins_list = list(all_origins)
        logger.debug(f"CORS origins loaded: {len(origins_list)} total")
        logger.debug(f"  - Environment origins: {len(env_origins)}")
        logger.debug(f"  - Default origins: {len(default_origins)}")
        logger.debug(f"  - Database origins: {len(db_origins)}")
        
        return origins_list
    
    async def _get_database_origins(self) -> Set[str]:
        """
        Get origins from database with caching.
        
        Returns:
            Set of origin URLs from database
        """
        now = datetime.now()
        
        # Check if cache is still valid
        if (now - self._last_refresh) < self._cache_duration and self._cached_origins:
            logger.debug("Using cached database origins")
            return self._cached_origins
        
        # Prevent concurrent refresh attempts
        if self._is_refreshing:
            logger.debug("Refresh already in progress, using cached origins")
            return self._cached_origins
        
        try:
            self._is_refreshing = True
            logger.debug("Refreshing database origins cache")
            
            # Get fresh data from database
            async with AsyncSessionLocal() as db:
                origins_list = await CorsService.get_active_origins_list(db)
                self._cached_origins = set(origins_list)
                self._last_refresh = now
                
            logger.debug(f"Refreshed database origins cache with {len(self._cached_origins)} origins")
            
        except Exception as e:
            logger.error(f"Error refreshing database origins: {e}")
            # Return cached origins on error to avoid disruption
            
        finally:
            self._is_refreshing = False
        
        return self._cached_origins
    
    def invalidate_cache(self):
        """Force cache invalidation on next request."""
        logger.debug("CORS origins cache invalidated")
        self._last_refresh = datetime.min
    
    async def refresh_cache(self):
        """Force immediate cache refresh."""
        logger.debug("Force refreshing CORS origins cache")
        self._last_refresh = datetime.min
        await self._get_database_origins()


# Global loader instance
cors_loader = CorsOriginsLoader()


async def get_cors_origins() -> List[str]:
    """
    Get all CORS origins for use in middleware.
    
    Returns:
        List of allowed origin URLs
    """
    return await cors_loader.get_all_origins()


def invalidate_cors_cache():
    """Invalidate the CORS origins cache."""
    cors_loader.invalidate_cache()


async def refresh_cors_cache():
    """Force refresh of CORS origins cache."""
    await cors_loader.refresh_cache()