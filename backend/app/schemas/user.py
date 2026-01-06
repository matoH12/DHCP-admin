"""
Pydantic schemas for User model
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional, Literal


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=6)
    role: Literal['RO', 'RW', 'ADMIN'] = 'RO'

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['RO', 'RW', 'ADMIN']:
            raise ValueError('Role must be RO, RW, or ADMIN')
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    is_active: Optional[bool] = None
    role: Optional[Literal['RO', 'RW', 'ADMIN']] = None

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v is not None and v not in ['RO', 'RW', 'ADMIN']:
            raise ValueError('Role must be RO, RW, or ADMIN')
        return v


class UserInDB(UserBase):
    """Schema for user in database"""
    id: int
    is_active: bool
    is_admin: bool
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserInDB):
    """Schema for user response (without sensitive data)"""
    pass
