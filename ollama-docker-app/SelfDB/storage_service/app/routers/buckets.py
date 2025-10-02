import logging
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any
import os
import json

from ..core.storage import storage
from ..apis.deps import get_current_user, TokenData

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.post("/{bucket_name}", status_code=status.HTTP_201_CREATED)
async def create_bucket(bucket_name: str) -> Dict[str, Any]:
    """
    Create a new bucket.
    """
    try:
        await storage.create_bucket(bucket_name)
        return {
            "status": "success",
            "message": f"Bucket '{bucket_name}' created successfully",
            "bucket_name": bucket_name
        }
    except Exception as e:
        logger.error(f"Error creating bucket '{bucket_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create bucket: {str(e)}"
        )

@router.get("/{bucket_name}/exists")
async def check_bucket_exists(bucket_name: str) -> Dict[str, Any]:
    """
    Check if a bucket exists.
    """
    exists = await storage.bucket_exists(bucket_name)
    return {
        "exists": exists,
        "bucket_name": bucket_name
    }

def get_bucket_metadata(bucket_name: str) -> dict:
    """Get bucket metadata from the metadata file"""
    from ..core.config import settings
    storage_path = settings.STORAGE_PATH
    metadata_path = os.path.join(storage_path, bucket_name, ".metadata.json")
    
    if not os.path.exists(metadata_path):
        return None
    
    try:
        with open(metadata_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error reading bucket metadata: {e}")
        return None

@router.delete("/{bucket_name}")
async def delete_bucket(
    bucket_name: str, 
    current_user: TokenData = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Delete a bucket and all its contents.
    Bucket owners and superusers can delete buckets.
    """
    try:
        # Check if bucket exists first
        bucket_exists = await storage.bucket_exists(bucket_name)
        if not bucket_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bucket '{bucket_name}' not found"
            )
        
        # Get bucket metadata to check ownership
        metadata = get_bucket_metadata(bucket_name)
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get bucket metadata"
            )
        
        # Check ownership or superuser permissions
        if metadata.get("owner_id") != current_user.sub and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this bucket"
            )
        
        result = await storage.delete_bucket(bucket_name)
        if result:
            return {
                "status": "success",
                "message": f"Bucket '{bucket_name}' deleted successfully",
                "bucket_name": bucket_name
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bucket '{bucket_name}' not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting bucket '{bucket_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete bucket: {str(e)}"
        )
