"""Pydantic schemas for CORS origin management."""

from pydantic import BaseModel, UUID4, Field
from typing import Optional, Dict, Any
from datetime import datetime


# Shared properties
class CorsOriginBase(BaseModel):
    origin: str = Field(..., description="The origin URL (e.g., https://app.example.com)")
    description: Optional[str] = Field(None, description="Optional description for this origin")
    is_active: bool = Field(True, description="Whether this origin is active")
    extra_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


# Properties to receive via API on creation
class CorsOriginCreate(BaseModel):
    origin: str = Field(..., description="The origin URL (e.g., https://app.example.com)")
    description: Optional[str] = Field(None, description="Optional description for this origin")
    extra_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


# Properties to receive via API on update
class CorsOriginUpdate(BaseModel):
    origin: Optional[str] = Field(None, description="The origin URL (e.g., https://app.example.com)")
    description: Optional[str] = Field(None, description="Optional description for this origin")
    is_active: Optional[bool] = Field(None, description="Whether this origin is active")
    extra_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


# Properties stored in DB
class CorsOriginInDB(CorsOriginBase):
    id: UUID4
    created_by: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Properties to return via API
class CorsOrigin(CorsOriginInDB):
    pass


# For origin validation responses
class CorsOriginValidation(BaseModel):
    origin: str
    is_valid: bool
    error_message: Optional[str] = None


# Response for listing origins
class CorsOriginsList(BaseModel):
    origins: list[CorsOrigin]
    total_count: int