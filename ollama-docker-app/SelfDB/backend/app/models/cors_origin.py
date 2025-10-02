from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid

from ..db.base_class import Base


class CorsOrigin(Base):
    """
    Represents a CORS origin configuration in the database.
    Allows dynamic management of allowed origins without server restarts.
    """
    __tablename__ = "cors_origins"

    # Columns definition
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    origin = Column(String, unique=True, index=True, nullable=False)  # e.g., "https://app.example.com"
    description = Column(Text, nullable=True)  # Optional description for documentation
    is_active = Column(Boolean(), default=True, index=True)  # Soft delete support
    extra_metadata = Column(JSON, nullable=True, default=dict)  # Additional metadata

    # User who created this origin
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship("User", back_populates="cors_origins")

    def __repr__(self):
        return f"<CorsOrigin(id={self.id}, origin='{self.origin}', is_active={self.is_active})>"