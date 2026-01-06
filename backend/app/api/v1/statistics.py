"""
Statistics API endpoints for DHCP Admin
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
from datetime import datetime, timedelta
import logging

from ...database import get_db
from ...dependencies import get_current_user
from ...models.user import User
from ...models.device import Device
from ...models.ip_range import IPRange
from ...models.syslog import SyslogMessage
from ...services.ip_range_service import get_ip_range_statistics
from ...services import device_history_service
from ...schemas.statistics import (
    ActivityTimelineResponse,
    DHCPEventsResponse,
    DHCPEventData,
    TopActiveDevicesResponse,
    TopActiveDevice
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/overview")
async def get_overview_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get overview statistics for the dashboard

    Returns:
        - Total IP ranges
        - Total devices
        - Total available IPs across all ranges
        - Total assigned IPs
        - Average utilization percentage
        - Active vs inactive devices
    """
    # Get all IP ranges
    ip_ranges = db.query(IPRange).filter(IPRange.is_active == True).all()
    total_ranges = len(ip_ranges)

    # Get all devices
    all_devices = db.query(Device).all()
    total_devices = len(all_devices)
    active_devices = len([d for d in all_devices if d.is_active])
    inactive_devices = total_devices - active_devices

    # Calculate IP statistics across all ranges
    total_usable_ips = 0
    total_assigned_ips = 0

    range_stats = []
    for ip_range in ip_ranges:
        stats = get_ip_range_statistics(db, ip_range.id)
        total_usable_ips += stats['total_usable']
        total_assigned_ips += stats['assigned']

        range_stats.append({
            'id': ip_range.id,
            'name': ip_range.name,
            'network': f"{ip_range.network_address}/{ip_range.cidr}",
            'assigned': stats['assigned'],
            'available': stats['available'],
            'utilization': stats['utilization_percent']
        })

    # Calculate overall utilization
    overall_utilization = (total_assigned_ips / total_usable_ips * 100) if total_usable_ips > 0 else 0

    return {
        'summary': {
            'total_ranges': total_ranges,
            'total_devices': total_devices,
            'active_devices': active_devices,
            'inactive_devices': inactive_devices,
            'total_usable_ips': total_usable_ips,
            'total_assigned_ips': total_assigned_ips,
            'total_available_ips': total_usable_ips - total_assigned_ips,
            'overall_utilization_percent': round(overall_utilization, 2)
        },
        'ranges': range_stats
    }


@router.get("/devices-by-range")
async def get_devices_by_range_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get device count grouped by IP range

    Useful for charts showing distribution of devices across ranges
    """
    ip_ranges = db.query(IPRange).filter(IPRange.is_active == True).all()

    data = []
    for ip_range in ip_ranges:
        device_count = db.query(Device).filter(
            Device.ip_range_id == ip_range.id,
            Device.is_active == True
        ).count()

        data.append({
            'range_name': ip_range.name,
            'network': f"{ip_range.network_address}/{ip_range.cidr}",
            'device_count': device_count
        })

    return {
        'data': data
    }


@router.get("/recent-devices")
async def get_recent_devices(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get recently added devices

    Args:
        limit: Number of devices to return (default 10)
    """
    devices = db.query(Device).order_by(
        Device.created_at.desc()
    ).limit(limit).all()

    result = []
    for device in devices:
        ip_range = db.query(IPRange).filter(IPRange.id == device.ip_range_id).first()
        result.append({
            'id': device.id,
            'hostname': device.hostname,
            'mac_address': device.mac_address,
            'ip_address': device.ip_address,
            'range_name': ip_range.name if ip_range else None,
            'created_at': device.created_at.isoformat(),
            'is_active': device.is_active
        })

    return {
        'devices': result
    }


@router.get("/device-activity-timeline", response_model=ActivityTimelineResponse)
async def get_device_activity_timeline(
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get device activity timeline for charts.

    Returns daily aggregated data showing how many devices were active each day.
    Used for area/line charts showing activity trends over time.

    Args:
        days: Number of days to look back (1-90)

    Returns:
        ActivityTimelineResponse with daily activity data
    """
    try:
        timeline_data, period_start, period_end = device_history_service.get_activity_timeline(db, days)

        return ActivityTimelineResponse(
            data=timeline_data,
            days=days,
            period_start=period_start,
            period_end=period_end
        )
    except Exception as e:
        logger.error(f"Failed to get activity timeline: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve activity timeline: {str(e)}")


@router.get("/dhcp-events", response_model=DHCPEventsResponse)
async def get_dhcp_events_stats(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get DHCP event statistics from syslog for pie chart visualization.

    Parses syslog messages to count DHCP events by type:
    - DISCOVER: Client searching for DHCP server
    - OFFER: Server offering IP address
    - REQUEST: Client requesting offered IP
    - ACK: Server acknowledging IP assignment
    - NAK: Server denying request

    Args:
        hours: Number of hours to analyze (1-168 = 7 days)

    Returns:
        DHCPEventsResponse with event counts and colors for charts
    """
    since = datetime.utcnow() - timedelta(hours=hours)

    # DHCP event types and their chart colors
    event_types = {
        'DISCOVER': '#8884d8',  # Blue
        'OFFER': '#82ca9d',     # Green
        'REQUEST': '#ffc658',   # Yellow
        'ACK': '#0088fe',       # Dark Blue
        'NAK': '#ff4d4f',       # Red
        'RELEASE': '#a4de6c'    # Light Green
    }

    try:
        data = []
        total_events = 0

        for event_type, color in event_types.items():
            # Count messages containing this DHCP event type
            count = db.query(SyslogMessage).filter(
                SyslogMessage.timestamp >= since,
                SyslogMessage.message.ilike(f'%DHCP{event_type}%')
            ).count()

            if count > 0:
                data.append(DHCPEventData(
                    name=event_type,
                    value=count,
                    color=color
                ))
                total_events += count

        return DHCPEventsResponse(
            data=data,
            total_events=total_events,
            time_range_hours=hours
        )

    except Exception as e:
        logger.error(f"Failed to get DHCP events: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve DHCP events: {str(e)}")


@router.get("/top-active-devices", response_model=TopActiveDevicesResponse)
async def get_top_active_devices(
    limit: int = Query(10, ge=5, le=50, description="Number of devices to return"),
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get most active devices based on DHCP activity.

    Ranks devices by number of DHCP events (ACK, REQUEST) recorded in DeviceHistory.
    Includes device details and IP range information.

    Args:
        limit: Number of top devices to return (5-50)
        days: Period to analyze (1-30 days)

    Returns:
        TopActiveDevicesResponse with ranked devices and activity counts
    """
    try:
        top_devices = device_history_service.get_top_active_devices(db, limit, days)

        # Convert to Pydantic models
        devices = [
            TopActiveDevice(
                device_id=d['device_id'],
                hostname=d['hostname'],
                ip_address=d['ip_address'],
                mac_address=d['mac_address'],
                activity_count=d['activity_count'],
                last_seen=d['last_seen'],
                range_name=d['range_name']
            )
            for d in top_devices
        ]

        return TopActiveDevicesResponse(
            data=devices,
            period_days=days
        )

    except Exception as e:
        logger.error(f"Failed to get top active devices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve top active devices: {str(e)}")
