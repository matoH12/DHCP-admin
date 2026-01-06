"""
IP Range service for CRUD operations
"""
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from ..models.ip_range import IPRange
from ..models.device import Device
from ..utils.ip_utils import calculate_range_statistics
from ..utils.validators import validate_network_address


def get_ip_ranges(db: Session, skip: int = 0, limit: int = 100) -> List[IPRange]:
    """Get list of IP ranges"""
    return db.query(IPRange).offset(skip).limit(limit).all()


def get_ip_range_by_id(db: Session, range_id: int) -> Optional[IPRange]:
    """Get IP range by ID"""
    return db.query(IPRange).filter(IPRange.id == range_id).first()


def get_ip_range_by_name(db: Session, name: str) -> Optional[IPRange]:
    """Get IP range by name"""
    return db.query(IPRange).filter(IPRange.name == name).first()


def create_ip_range(
    db: Session,
    name: str,
    network_address: str,
    cidr: int,
    gateway: Optional[str] = None,
    dns_servers: Optional[List[str]] = None,
    domain_name: Optional[str] = None,
    description: Optional[str] = None,
    pool_start: Optional[str] = None,
    pool_end: Optional[str] = None
) -> IPRange:
    """
    Create a new IP range

    Args:
        db: Database session
        name: Range name
        network_address: Network address (e.g., "192.168.1.0")
        cidr: CIDR notation (e.g., 24)
        gateway: Gateway IP address
        dns_servers: List of DNS server IPs
        domain_name: Domain name
        description: Description

    Returns:
        Created IP range
    """
    # Validate network address
    is_valid, error = validate_network_address(network_address, cidr)
    if not is_valid:
        raise ValueError(error)

    # Convert DNS servers list to JSON string
    dns_json = json.dumps(dns_servers) if dns_servers else None

    ip_range = IPRange(
        name=name,
        network_address=network_address,
        cidr=cidr,
        gateway=gateway,
        dns_servers=dns_json,
        domain_name=domain_name,
        description=description,
        pool_start=pool_start,
        pool_end=pool_end,
        is_active=True,
    )
    db.add(ip_range)
    db.commit()
    db.refresh(ip_range)
    return ip_range


def update_ip_range(
    db: Session,
    range_id: int,
    **kwargs
) -> Optional[IPRange]:
    """
    Update an IP range

    Args:
        db: Database session
        range_id: IP range ID
        **kwargs: Fields to update

    Returns:
        Updated IP range or None if not found
    """
    ip_range = get_ip_range_by_id(db, range_id)
    if not ip_range:
        return None

    # Handle DNS servers conversion
    if 'dns_servers' in kwargs and kwargs['dns_servers'] is not None:
        kwargs['dns_servers'] = json.dumps(kwargs['dns_servers'])

    for key, value in kwargs.items():
        if value is not None and hasattr(ip_range, key):
            setattr(ip_range, key, value)

    db.commit()
    db.refresh(ip_range)
    return ip_range


def delete_ip_range(db: Session, range_id: int) -> bool:
    """
    Delete an IP range

    Args:
        db: Database session
        range_id: IP range ID

    Returns:
        True if deleted, False if not found
    """
    ip_range = get_ip_range_by_id(db, range_id)
    if not ip_range:
        return False

    db.delete(ip_range)
    db.commit()
    return True


def get_ip_range_statistics(db: Session, range_id: int) -> Optional[dict]:
    """
    Get usage statistics for an IP range

    Args:
        db: Database session
        range_id: IP range ID

    Returns:
        Statistics dictionary or None if range not found
    """
    ip_range = get_ip_range_by_id(db, range_id)
    if not ip_range:
        return None

    # Count assigned devices in this range
    assigned_count = db.query(Device)\
        .filter(Device.ip_range_id == range_id)\
        .filter(Device.is_active == True)\
        .count()

    # Calculate statistics
    stats = calculate_range_statistics(
        ip_range.network_address,
        ip_range.cidr,
        assigned_count,
        ip_range.gateway
    )

    return stats


def get_available_ips_in_range(db: Session, range_id: int) -> List[str]:
    """
    Get list of available IP addresses in a range

    Args:
        db: Database session
        range_id: IP range ID

    Returns:
        List of available IP addresses
    """
    from ..utils.ip_utils import get_available_ips

    ip_range = get_ip_range_by_id(db, range_id)
    if not ip_range:
        return []

    # Get all assigned IPs in this range
    assigned_devices = db.query(Device.ip_address)\
        .filter(Device.ip_range_id == range_id)\
        .filter(Device.is_active == True)\
        .all()

    assigned_ips = set(device[0] for device in assigned_devices)

    # Get available IPs
    available = get_available_ips(
        ip_range.network_address,
        ip_range.cidr,
        assigned_ips,
        ip_range.gateway
    )

    return available
