from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Base schemas
class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class PromptBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    category_id: Optional[int] = None
    tag_names: List[str] = Field(default_factory=list)

# Create schemas
class TagCreate(TagBase):
    pass

class CategoryCreate(CategoryBase):
    pass

class PromptCreate(PromptBase):
    pass

# Update schemas
class TagUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None

class PromptUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    content: Optional[str] = Field(default=None, min_length=1)
    category_id: Optional[int] = None
    tag_names: Optional[List[str]] = None

# Response schemas
class TagResponse(TagBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PromptResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    category_id: Optional[int] = None
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = Field(default_factory=list)
    tag_names: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def set_tag_names(self) -> 'PromptResponse':
        if self.tags and not self.tag_names:
            self.tag_names = [tag.name for tag in self.tags]
        return self

# Utility schemas
class Message(BaseModel):
    detail: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
