"""API endpoints for CORS origin management."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.cors import (
    CorsOrigin,
    CorsOriginCreate,
    CorsOriginUpdate,
    CorsOriginValidation,
    CorsOriginsList
)
from ...models.user import User
from ...services.cors_service import CorsService
from ...core.cors_loader import refresh_cors_cache
from ..deps import get_db, get_current_active_superuser


router = APIRouter()


@router.get("/", response_model=CorsOriginsList)
async def list_cors_origins(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    active_only: bool = True,
) -> CorsOriginsList:
    """
    List all CORS origins.
    Requires superuser privileges.
    """
    origins = await CorsService.list_origins(db, active_only=active_only)
    return CorsOriginsList(
        origins=[CorsOrigin.model_validate(origin) for origin in origins],
        total_count=len(origins)
    )


@router.post("/", response_model=CorsOrigin, status_code=status.HTTP_201_CREATED)
async def create_cors_origin(
    *,
    db: AsyncSession = Depends(get_db),
    origin_data: CorsOriginCreate,
    current_user: User = Depends(get_current_active_superuser),
) -> CorsOrigin:
    """
    Create a new CORS origin.
    Requires superuser privileges.
    """
    origin = await CorsService.create_origin(db, origin_data, current_user)
    await db.commit()
    return CorsOrigin.model_validate(origin)


@router.get("/{origin_id}", response_model=CorsOrigin)
async def get_cors_origin(
    *,
    db: AsyncSession = Depends(get_db),
    origin_id: UUID,
    current_user: User = Depends(get_current_active_superuser),
) -> CorsOrigin:
    """
    Get a specific CORS origin by ID.
    Requires superuser privileges.
    """
    origin = await CorsService.get_origin_by_id(db, str(origin_id))
    if not origin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Origin not found"
        )
    return CorsOrigin.model_validate(origin)


@router.put("/{origin_id}", response_model=CorsOrigin)
async def update_cors_origin(
    *,
    db: AsyncSession = Depends(get_db),
    origin_id: UUID,
    origin_data: CorsOriginUpdate,
    current_user: User = Depends(get_current_active_superuser),
) -> CorsOrigin:
    """
    Update a CORS origin.
    Requires superuser privileges.
    """
    origin = await CorsService.update_origin(db, str(origin_id), origin_data, current_user)
    await db.commit()
    return CorsOrigin.model_validate(origin)


@router.delete("/{origin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cors_origin(
    *,
    db: AsyncSession = Depends(get_db),
    origin_id: UUID,
    current_user: User = Depends(get_current_active_superuser),
    hard_delete: bool = False,
) -> None:
    """
    Delete a CORS origin.
    By default performs soft delete (sets is_active=False).
    Use hard_delete=True to permanently remove.
    Requires superuser privileges.
    """
    if hard_delete:
        deleted = await CorsService.hard_delete_origin(db, str(origin_id))
    else:
        deleted = await CorsService.delete_origin(db, str(origin_id))
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Origin not found"
        )
    
    await db.commit()


@router.post("/validate", response_model=CorsOriginValidation)
async def validate_cors_origin(
    *,
    origin: str,
    current_user: User = Depends(get_current_active_superuser),
) -> CorsOriginValidation:
    """
    Validate a CORS origin URL format.
    Requires superuser privileges.
    """
    is_valid = CorsService.validate_origin(origin)
    error_message = None if is_valid else "Invalid origin URL format"
    
    return CorsOriginValidation(
        origin=origin,
        is_valid=is_valid,
        error_message=error_message
    )


@router.post("/refresh-cache", status_code=status.HTTP_200_OK)
async def refresh_cors_cache_endpoint(
    *,
    current_user: User = Depends(get_current_active_superuser),
) -> dict:
    """
    Manually refresh the CORS origins cache.
    Useful for testing or troubleshooting.
    Requires superuser privileges.
    """
    await refresh_cors_cache()
    return {"message": "CORS origins cache refreshed successfully"}