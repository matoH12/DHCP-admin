"""
Pydantic schemas for DHCP Config
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DHCPConfigBase(BaseModel):
    """Base DHCP config schema"""
    version: int
    file_path: str


class DHCPConfig(DHCPConfigBase):
    """Schema for DHCP config response"""
    id: int
    config_content: str
    generated_at: datetime
    generated_by: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True


class DHCPConfigSummary(DHCPConfigBase):
    """Summary schema for DHCP config (without full content)"""
    id: int
    generated_at: datetime
    generated_by: Optional[int] = None
    is_active: bool
    content_length: int

    class Config:
        from_attributes = True


class DHCPGenerateResponse(BaseModel):
    """Response schema for config generation"""
    message: str
    version: int
    file_path: str
    generated_at: datetime
