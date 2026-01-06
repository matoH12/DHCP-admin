"""
Pydantic schemas for Device model
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from ..utils.validators import validate_hostname, validate_mac_address, validate_ip_address, normalize_mac_address


class DeviceBase(BaseModel):
    """Base device schema"""
    hostname: str = Field(..., min_length=1, max_length=63)
    mac_address: str
    ip_address: str
    ip_range_id: Optional[int] = None
    description: Optional[str] = None

    @field_validator('hostname')
    @classmethod
    def validate_hostname_format(cls, v):
        is_valid, error = validate_hostname(v)
        if not is_valid:
            raise ValueError(error)
        return v

    @field_validator('mac_address')
    @classmethod
    def validate_and_normalize_mac(cls, v):
        is_valid, error = validate_mac_address(v)
        if not is_valid:
            raise ValueError(error)
        # Normalize to XX:XX:XX:XX:XX:XX format
        return normalize_mac_address(v)

    @field_validator('ip_address')
    @classmethod
    def validate_ip(cls, v):
        is_valid, error = validate_ip_address(v)
        if not is_valid:
            raise ValueError(error)
        return v


class DeviceCreate(DeviceBase):
    """Schema for creating a device"""
    pass


class DeviceUpdate(BaseModel):
    """Schema for updating a device"""
    hostname: Optional[str] = Field(None, min_length=1, max_length=63)
    mac_address: Optional[str] = None
    ip_address: Optional[str] = None
    ip_range_id: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator('hostname')
    @classmethod
    def validate_hostname_format(cls, v):
        if v is not None:
            is_valid, error = validate_hostname(v)
            if not is_valid:
                raise ValueError(error)
        return v

    @field_validator('mac_address')
    @classmethod
    def validate_and_normalize_mac(cls, v):
        if v is not None:
            is_valid, error = validate_mac_address(v)
            if not is_valid:
                raise ValueError(error)
            return normalize_mac_address(v)
        return v

    @field_validator('ip_address')
    @classmethod
    def validate_ip(cls, v):
        if v is not None:
            is_valid, error = validate_ip_address(v)
            if not is_valid:
                raise ValueError(error)
        return v


class Device(DeviceBase):
    """Schema for device response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    last_seen: Optional[datetime] = None  # Last activity from DHCP logs

    class Config:
        from_attributes = True


class DeviceSearch(BaseModel):
    """Schema for device search filters"""
    query: Optional[str] = None  # Search in hostname, MAC, IP
    ip_range_id: Optional[int] = None
    is_active: Optional[bool] = None
