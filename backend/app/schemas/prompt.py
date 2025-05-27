from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class PromptBase(BaseModel):
    """Base schema for prompts"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    prompt_text: str = Field(..., min_length=1)
    category_id: int
    tags: List[str] = Field(default_factory=list)

class PromptCreate(PromptBase):
    """Schema for creating a new prompt"""
    pass

class PromptUpdate(BaseModel):
    """Schema for updating a prompt"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    prompt_text: Optional[str] = Field(None, min_length=1)
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None

class PromptInDBBase(PromptBase):
    """Base schema for prompt in database"""
    id: int
    created_at: datetime
    updated_at: datetime
    like_count: int = 0
    user_id: int

    class Config:
        from_attributes = True

class Prompt(PromptInDBBase):
    """Schema for prompt responses"""
    pass

class PromptResponse(Prompt):
    """Schema for prompt responses with additional fields"""
    is_liked: bool = False
    like_count: int = 0
    tags: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)

class PromptWithLikes(PromptInDBBase):
    """Schema for prompt with like information"""
    is_liked: bool = False
    like_count: int = 0
