from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class TagBase(BaseModel):
    """Base schema for tags"""
    name: str = Field(..., min_length=1, max_length=50)

class TagCreate(TagBase):
    """Schema for creating a new tag"""
    pass

class TagUpdate(BaseModel):
    """Schema for updating a tag"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)

class TagInDBBase(TagBase):
    """Base schema for tag in database"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Tag(TagInDBBase):
    """Schema for tag responses"""
    pass

class TagResponse(TagInDBBase):
    """Schema for tag responses with additional fields"""
    prompt_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)
