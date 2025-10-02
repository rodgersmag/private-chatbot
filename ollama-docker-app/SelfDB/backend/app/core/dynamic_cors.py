"""Dynamic CORS middleware for SelfDB."""

import asyncio
from typing import List
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
import logging

from .cors_loader import get_cors_origins

logger = logging.getLogger(__name__)


class DynamicCORSMiddleware(BaseHTTPMiddleware):
    """
    Dynamic CORS middleware that loads allowed origins from database and environment variables.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        allow_credentials: bool = True,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
        expose_headers: List[str] = None,
        max_age: int = 86400,
    ):
        super().__init__(app)
        self.allow_credentials = allow_credentials
        self.allow_methods = allow_methods or ["*"]
        self.allow_headers = allow_headers or ["*"]
        self.expose_headers = expose_headers or []
        self.max_age = max_age
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process CORS for each request."""
        origin = request.headers.get("origin")
        
        # Handle preflight requests
        if request.method == "OPTIONS" and origin:
            return await self._handle_preflight(request, origin)
        
        # Process regular request
        response = await call_next(request)
        
        # Add CORS headers to response
        if origin:
            await self._add_cors_headers(response, origin)
        
        return response
    
    async def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed by loading from dynamic sources."""
        try:
            allowed_origins = await get_cors_origins()
            
            # Check for exact match
            if origin in allowed_origins:
                return True
            
            # Check for wildcard match (though we discourage this in production)
            if "*" in allowed_origins:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking origin {origin}: {e}")
            # In case of error, deny access for security
            return False
    
    async def _handle_preflight(self, request: Request, origin: str) -> Response:
        """Handle CORS preflight requests."""
        if not await self._is_origin_allowed(origin):
            logger.warning(f"CORS preflight rejected for origin: {origin}")
            return Response(status_code=403, content="CORS origin not allowed")
        
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": ", ".join(self.allow_methods),
            "Access-Control-Allow-Headers": ", ".join(self.allow_headers),
            "Access-Control-Max-Age": str(self.max_age),
        }
        
        if self.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"
        
        if self.expose_headers:
            headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)
        
        logger.debug(f"CORS preflight approved for origin: {origin}")
        return Response(status_code=200, headers=headers)
    
    async def _add_cors_headers(self, response: Response, origin: str):
        """Add CORS headers to regular responses."""
        if not await self._is_origin_allowed(origin):
            logger.warning(f"CORS response blocked for origin: {origin}")
            return
        
        response.headers["Access-Control-Allow-Origin"] = origin
        
        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        if self.expose_headers:
            response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)
        
        logger.debug(f"CORS headers added for origin: {origin}")