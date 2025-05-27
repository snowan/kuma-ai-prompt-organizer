from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class CategoryBase(BaseModel):
    """Base schema for categories"""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""
    pass

class CategoryUpdate(BaseModel):
    """Schema for updating a category"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None

class CategoryInDBBase(CategoryBase):
    """Base schema for category in database"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Category(CategoryInDBBase):
    """Schema for category responses"""
    pass

class CategoryResponse(Category):
    """Schema for category responses with additional fields"""
    prompt_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)
