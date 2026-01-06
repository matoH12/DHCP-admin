"""
Statistics API endpoints for DHCP Admin
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from ...database import get_db
from ...dependencies import get_current_user
from ...models.user import User
from ...models.device import Device
from ...models.ip_range import IPRange
from ...services.ip_range_service import get_ip_range_statistics

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
