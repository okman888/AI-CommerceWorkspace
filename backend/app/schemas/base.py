"""Base Pydantic schemas."""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class TimestampSchema(BaseModel):
    """Base schema with timestamp fields."""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IDSchema(BaseModel):
    """Base schema with id field."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
