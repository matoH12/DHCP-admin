"""
Pydantic schemas for IPRange model
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from ..utils.validators import validate_cidr, validate_network_address, validate_ip_address


class IPRangeBase(BaseModel):
    """Base IP range schema"""
    name: str = Field(..., min_length=1, max_length=100)
    network_address: str
    cidr: int = Field(..., ge=8, le=30)
    gateway: Optional[str] = None
    dns_servers: Optional[List[str]] = None
    domain_name: Optional[str] = None
    description: Optional[str] = None
    pool_start: Optional[str] = None
    pool_end: Optional[str] = None

    @field_validator('cidr')
    @classmethod
    def validate_cidr_value(cls, v):
        is_valid, error = validate_cidr(v)
        if not is_valid:
            raise ValueError(error)
        return v

    @field_validator('gateway')
    @classmethod
    def validate_gateway_ip(cls, v):
        if v is not None:
            is_valid, error = validate_ip_address(v)
            if not is_valid:
                raise ValueError(error)
        return v

    @field_validator('pool_end')
    @classmethod
    def validate_pool_in_subnet(cls, v, info):
        """Validate that pool IPs are within the subnet"""
        if v is None:
            return v

        # Get other field values
        pool_start = info.data.get('pool_start')
        network_address = info.data.get('network_address')
        cidr = info.data.get('cidr')

        # If pool_start is set, validate both are in subnet
        if pool_start and network_address and cidr:
            from ipaddress import IPv4Network, IPv4Address

            # Validate IP formats
            is_valid, error = validate_ip_address(pool_start)
            if not is_valid:
                raise ValueError(f"Pool start: {error}")

            is_valid, error = validate_ip_address(v)
            if not is_valid:
                raise ValueError(f"Pool end: {error}")

            # Check if IPs are in subnet
            network = IPv4Network(f"{network_address}/{cidr}", strict=False)
            pool_start_ip = IPv4Address(pool_start)
            pool_end_ip = IPv4Address(v)

            if pool_start_ip not in network:
                raise ValueError(f"Pool start {pool_start} nie je v sieti {network}")

            if pool_end_ip not in network:
                raise ValueError(f"Pool end {v} nie je v sieti {network}")

            # Check if pool_start < pool_end
            if pool_start_ip >= pool_end_ip:
                raise ValueError("Pool start musí byť menší ako pool end")

        return v


class IPRangeCreate(IPRangeBase):
    """Schema for creating an IP range"""
    pass


class IPRangeUpdate(BaseModel):
    """Schema for updating an IP range"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    gateway: Optional[str] = None
    dns_servers: Optional[List[str]] = None
    domain_name: Optional[str] = None
    description: Optional[str] = None
    pool_start: Optional[str] = None
    pool_end: Optional[str] = None
    is_active: Optional[bool] = None


class IPRange(IPRangeBase):
    """Schema for IP range response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @field_validator('dns_servers', mode='before')
    @classmethod
    def parse_dns_servers(cls, v):
        """Convert JSON string to list if needed"""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except:
                return []
        return v

    class Config:
        from_attributes = True


class IPRangeWithStats(IPRange):
    """IP range with usage statistics"""
    total_usable: int
    assigned: int
    available: int
    utilization_percent: float
