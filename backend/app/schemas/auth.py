from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    """Schema for JWT token"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token data"""
    username: Optional[str] = None

class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, max_length=100)

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str

class UserInDB(UserBase):
    """User schema for database operations"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserResponse(UserInDB):
    """Schema for user responses (excludes sensitive data)"""
    pass

class LikeBase(BaseModel):
    """Base like schema"""
    user_id: int
    prompt_id: int

class LikeCreate(LikeBase):
    """Schema for creating a like"""
    pass

class LikeResponse(LikeBase):
    """Schema for like responses"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
