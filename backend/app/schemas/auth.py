"""
Pydantic schemas for authentication
"""
from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str
    password: str


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data"""
    username: str
    user_id: int
