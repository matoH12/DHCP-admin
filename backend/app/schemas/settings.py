"""
Pydantic schemas for Settings
"""
from pydantic import BaseModel, Field
from typing import Optional


class SettingUpdate(BaseModel):
    """Schema for updating a setting"""
    value: str = Field(..., min_length=1)


class Setting(BaseModel):
    """Schema for setting response"""
    key: str
    value: str
    description: Optional[str] = None

    class Config:
        from_attributes = True
