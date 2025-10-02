"""CORS origins management service."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from fastapi import HTTPException, status
import re

from ..models.cors_origin import CorsOrigin
from ..models.user import User
from ..schemas.cors import CorsOriginCreate, CorsOriginUpdate


class CorsService:
    """Service for managing CORS origins."""

    @staticmethod
    def validate_origin(origin: str) -> bool:
        """
        Validate that an origin URL is properly formatted.
        
        Args:
            origin: The origin URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not origin:
            return False
            
        # Allow localhost variations (with or without port)
        localhost_pattern = r'^https?://localhost(:[0-9]{1,5})?$'
        if re.match(localhost_pattern, origin):
            return True
        
        # Allow IP addresses (IPv4)
        ip_pattern = r'^https?://(\d{1,3}\.){3}\d{1,3}(:[0-9]{1,5})?$'
        if re.match(ip_pattern, origin):
            return True
            
        # For regular domains, require at least one dot (TLD)
        # Pattern: protocol://domain.tld[:port]
        domain_pattern = r'^https?://[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+?(:[0-9]{1,5})?$'
        
        return bool(re.match(domain_pattern, origin))

    @staticmethod
    async def list_origins(db: AsyncSession, active_only: bool = True) -> List[CorsOrigin]:
        """
        Get all CORS origins from the database.
        
        Args:
            db: Database session
            active_only: If True, only return active origins
            
        Returns:
            List of CorsOrigin objects
        """
        query = select(CorsOrigin)
        if active_only:
            query = query.where(CorsOrigin.is_active == True)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_origin_by_id(db: AsyncSession, origin_id: str) -> Optional[CorsOrigin]:
        """
        Get a CORS origin by ID.
        
        Args:
            db: Database session
            origin_id: The UUID of the origin
            
        Returns:
            CorsOrigin object or None if not found
        """
        query = select(CorsOrigin).where(CorsOrigin.id == origin_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_origin_by_url(db: AsyncSession, origin_url: str) -> Optional[CorsOrigin]:
        """
        Get a CORS origin by URL.
        
        Args:
            db: Database session
            origin_url: The origin URL
            
        Returns:
            CorsOrigin object or None if not found
        """
        query = select(CorsOrigin).where(CorsOrigin.origin == origin_url)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_origin(
        db: AsyncSession, 
        origin_data: CorsOriginCreate, 
        user: User
    ) -> CorsOrigin:
        """
        Create a new CORS origin.
        
        Args:
            db: Database session
            origin_data: CORS origin creation data
            user: User creating the origin
            
        Returns:
            Created CorsOrigin object
            
        Raises:
            HTTPException: If origin is invalid or already exists
        """
        # Validate origin URL
        if not CorsService.validate_origin(origin_data.origin):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid origin URL format"
            )
        
        # Check if origin already exists
        existing = await CorsService.get_origin_by_url(db, origin_data.origin)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Origin already exists"
            )
        
        # Create new origin
        db_origin = CorsOrigin(
            origin=origin_data.origin,
            description=origin_data.description,
            extra_metadata=origin_data.extra_metadata or {},
            created_by=user.id
        )
        
        db.add(db_origin)
        await db.flush()
        await db.refresh(db_origin)
        
        # Invalidate CORS cache after creating new origin
        from ..core.cors_loader import invalidate_cors_cache
        invalidate_cors_cache()
        
        return db_origin

    @staticmethod
    async def update_origin(
        db: AsyncSession,
        origin_id: str,
        origin_data: CorsOriginUpdate,
        user: User
    ) -> CorsOrigin:
        """
        Update an existing CORS origin.
        
        Args:
            db: Database session
            origin_id: ID of the origin to update
            origin_data: Updated origin data
            user: User updating the origin
            
        Returns:
            Updated CorsOrigin object
            
        Raises:
            HTTPException: If origin not found or validation fails
        """
        # Get existing origin
        origin = await CorsService.get_origin_by_id(db, origin_id)
        if not origin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Origin not found"
            )
        
        # Validate new origin URL if provided
        if origin_data.origin and not CorsService.validate_origin(origin_data.origin):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid origin URL format"
            )
        
        # Check for duplicate origin if changing URL
        if origin_data.origin and origin_data.origin != origin.origin:
            existing = await CorsService.get_origin_by_url(db, origin_data.origin)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Origin already exists"
                )
        
        # Update fields
        update_data = {}
        if origin_data.origin is not None:
            update_data["origin"] = origin_data.origin
        if origin_data.description is not None:
            update_data["description"] = origin_data.description
        if origin_data.is_active is not None:
            update_data["is_active"] = origin_data.is_active
        if origin_data.extra_metadata is not None:
            update_data["extra_metadata"] = origin_data.extra_metadata
        
        if update_data:
            query = update(CorsOrigin).where(CorsOrigin.id == origin_id).values(**update_data)
            await db.execute(query)
            await db.refresh(origin)
            
            # Invalidate CORS cache after updating origin
            from ..core.cors_loader import invalidate_cors_cache
            invalidate_cors_cache()
        
        return origin

    @staticmethod
    async def delete_origin(db: AsyncSession, origin_id: str) -> bool:
        """
        Soft delete a CORS origin by setting is_active to False.
        
        Args:
            db: Database session
            origin_id: ID of the origin to delete
            
        Returns:
            True if deleted, False if not found
        """
        origin = await CorsService.get_origin_by_id(db, origin_id)
        if not origin:
            return False
        
        query = update(CorsOrigin).where(CorsOrigin.id == origin_id).values(is_active=False)
        await db.execute(query)
        
        # Invalidate CORS cache after soft deleting origin
        from ..core.cors_loader import invalidate_cors_cache
        invalidate_cors_cache()
        
        return True

    @staticmethod
    async def hard_delete_origin(db: AsyncSession, origin_id: str) -> bool:
        """
        Permanently delete a CORS origin.
        
        Args:
            db: Database session
            origin_id: ID of the origin to delete
            
        Returns:
            True if deleted, False if not found
        """
        origin = await CorsService.get_origin_by_id(db, origin_id)
        if not origin:
            return False
        
        query = delete(CorsOrigin).where(CorsOrigin.id == origin_id)
        await db.execute(query)
        
        # Invalidate CORS cache after hard deleting origin
        from ..core.cors_loader import invalidate_cors_cache
        invalidate_cors_cache()
        
        return True

    @staticmethod
    async def get_active_origins_list(db: AsyncSession) -> List[str]:
        """
        Get a list of active origin URLs for use in CORS middleware.
        
        Args:
            db: Database session
            
        Returns:
            List of origin URL strings
        """
        origins = await CorsService.list_origins(db, active_only=True)
        return [origin.origin for origin in origins]