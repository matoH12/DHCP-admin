"""
Pydantic schemas for Syslog model
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SyslogMessageBase(BaseModel):
    """Base syslog message schema"""
    timestamp: datetime
    facility: Optional[str] = None
    severity: Optional[str] = None
    hostname: Optional[str] = None
    source_ip: Optional[str] = None
    program: Optional[str] = None
    message: str
    raw_message: Optional[str] = None


class SyslogMessage(SyslogMessageBase):
    """Schema for syslog message response"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
