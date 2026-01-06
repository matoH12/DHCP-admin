"""
Statistics API Response Schemas

Pydantic models for analytics and dashboard statistics endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ========== Activity Timeline ==========

class ActivityTimelinePoint(BaseModel):
    """Single data point in activity timeline"""
    date: str = Field(..., description="Date in ISO format (YYYY-MM-DD)")
    active_devices: int = Field(..., ge=0, description="Number of distinct active devices on this date")
    total_events: int = Field(..., ge=0, description="Total DHCP events on this date")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2026-01-06",
                "active_devices": 15,
                "total_events": 45
            }
        }


class ActivityTimelineResponse(BaseModel):
    """Device activity timeline for charts"""
    data: List[ActivityTimelinePoint] = Field(..., description="Daily activity data points")
    days: int = Field(..., ge=1, le=90, description="Number of days in period")
    period_start: datetime = Field(..., description="Start of analysis period")
    period_end: datetime = Field(..., description="End of analysis period")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {"date": "2026-01-01", "active_devices": 12, "total_events": 34},
                    {"date": "2026-01-02", "active_devices": 15, "total_events": 42}
                ],
                "days": 7,
                "period_start": "2026-01-01T00:00:00Z",
                "period_end": "2026-01-07T23:59:59Z"
            }
        }


# ========== DHCP Events ==========

class DHCPEventData(BaseModel):
    """DHCP event count with color for pie chart"""
    name: str = Field(..., description="DHCP event type (DISCOVER, OFFER, REQUEST, ACK, NAK)")
    value: int = Field(..., ge=0, description="Number of events")
    color: str = Field(..., description="Hex color code for chart display")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "ACK",
                "value": 150,
                "color": "#0088fe"
            }
        }


class DHCPEventsResponse(BaseModel):
    """DHCP events statistics from syslog"""
    data: List[DHCPEventData] = Field(..., description="Event counts by type")
    total_events: int = Field(..., ge=0, description="Total events across all types")
    time_range_hours: int = Field(..., ge=1, le=168, description="Analysis period in hours")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {"name": "DISCOVER", "value": 150, "color": "#8884d8"},
                    {"name": "OFFER", "value": 148, "color": "#82ca9d"},
                    {"name": "REQUEST", "value": 145, "color": "#ffc658"},
                    {"name": "ACK", "value": 143, "color": "#0088fe"},
                    {"name": "NAK", "value": 2, "color": "#ff4d4f"}
                ],
                "total_events": 588,
                "time_range_hours": 24
            }
        }


# ========== Top Active Devices ==========

class TopActiveDevice(BaseModel):
    """Device with activity metrics"""
    device_id: int = Field(..., description="Device database ID")
    hostname: str = Field(..., description="Device hostname")
    ip_address: str = Field(..., description="Current IP address")
    mac_address: str = Field(..., description="MAC address")
    activity_count: int = Field(..., ge=0, description="Number of DHCP events in period")
    last_seen: Optional[datetime] = Field(None, description="Last seen timestamp")
    range_name: Optional[str] = Field(None, description="IP range name")

    class Config:
        json_schema_extra = {
            "example": {
                "device_id": 1,
                "hostname": "server-01",
                "ip_address": "192.168.1.10",
                "mac_address": "aa:bb:cc:dd:ee:ff",
                "activity_count": 45,
                "last_seen": "2026-01-06T12:00:00Z",
                "range_name": "Production Network"
            }
        }


class TopActiveDevicesResponse(BaseModel):
    """Top active devices ranking"""
    data: List[TopActiveDevice] = Field(..., description="Devices ranked by activity")
    period_days: int = Field(..., ge=1, le=30, description="Analysis period in days")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "device_id": 1,
                        "hostname": "server-01",
                        "ip_address": "192.168.1.10",
                        "mac_address": "aa:bb:cc:dd:ee:ff",
                        "activity_count": 45,
                        "last_seen": "2026-01-06T12:00:00Z",
                        "range_name": "Production"
                    }
                ],
                "period_days": 7
            }
        }


# ========== Chart Data (for overview endpoint extension) ==========

class ChartUtilizationData(BaseModel):
    """IP range utilization for bar chart"""
    name: str = Field(..., description="Range name")
    assigned: int = Field(..., ge=0, description="Number of assigned IPs")
    available: int = Field(..., ge=0, description="Number of available IPs")
    utilization: float = Field(..., ge=0, le=100, description="Utilization percentage")
    total: int = Field(..., ge=0, description="Total usable IPs")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Production",
                "assigned": 45,
                "available": 55,
                "utilization": 45.0,
                "total": 100
            }
        }
