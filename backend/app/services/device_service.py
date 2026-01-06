"""
Device service for CRUD operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from ..models.device import Device
from ..models.ip_range import IPRange
from ..utils.validators import validate_ip_in_range, normalize_mac_address
from ..utils.ip_utils import suggest_next_ip


def get_devices(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    ip_range_id: Optional[int] = None,
    is_active: Optional[bool] = None
) -> List[Device]:
    """
    Get list of devices with optional filters

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search query (searches hostname, MAC, IP)
        ip_range_id: Filter by IP range
        is_active: Filter by active status

    Returns:
        List of devices
    """
    query = db.query(Device)

    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Device.hostname.ilike(search_pattern),
                Device.mac_address.ilike(search_pattern),
                Device.ip_address.ilike(search_pattern),
                Device.description.ilike(search_pattern)
            )
        )

    # Apply IP range filter
    if ip_range_id is not None:
        query = query.filter(Device.ip_range_id == ip_range_id)

    # Apply active status filter
    if is_active is not None:
        query = query.filter(Device.is_active == is_active)

    return query.offset(skip).limit(limit).all()


def get_device_by_id(db: Session, device_id: int) -> Optional[Device]:
    """Get device by ID"""
    return db.query(Device).filter(Device.id == device_id).first()


def get_device_by_hostname(db: Session, hostname: str) -> Optional[Device]:
    """Get device by hostname"""
    return db.query(Device).filter(Device.hostname == hostname).first()


def get_device_by_mac(db: Session, mac_address: str) -> Optional[Device]:
    """Get device by MAC address"""
    # Normalize MAC address before searching
    normalized_mac = normalize_mac_address(mac_address)
    return db.query(Device).filter(Device.mac_address == normalized_mac).first()


def get_device_by_ip(db: Session, ip_address: str) -> Optional[Device]:
    """Get device by IP address"""
    return db.query(Device).filter(Device.ip_address == ip_address).first()


def create_device(
    db: Session,
    hostname: str,
    mac_address: str,
    ip_address: str,
    ip_range_id: Optional[int] = None,
    description: Optional[str] = None,
    user_id: Optional[int] = None
) -> Device:
    """
    Create a new device

    Args:
        db: Database session
        hostname: Device hostname
        mac_address: MAC address (will be normalized)
        ip_address: IP address
        ip_range_id: Optional IP range ID
        description: Optional description
        user_id: ID of user creating the device

    Returns:
        Created device

    Raises:
        ValueError: If validation fails or duplicates exist
    """
    # Normalize MAC address
    mac_address = normalize_mac_address(mac_address)

    # Check for duplicates
    if get_device_by_hostname(db, hostname):
        raise ValueError(f"Device with hostname '{hostname}' already exists")

    if get_device_by_mac(db, mac_address):
        raise ValueError(f"Device with MAC address '{mac_address}' already exists")

    if get_device_by_ip(db, ip_address):
        raise ValueError(f"Device with IP address '{ip_address}' already exists")

    # Validate IP is in range (if range specified)
    if ip_range_id:
        ip_range = db.query(IPRange).filter(IPRange.id == ip_range_id).first()
        if not ip_range:
            raise ValueError(f"IP range with ID {ip_range_id} not found")

        is_valid, error = validate_ip_in_range(
            ip_address,
            ip_range.network_address,
            ip_range.cidr
        )
        if not is_valid:
            raise ValueError(error)

        # Check if IP is gateway
        if ip_range.gateway and ip_address == ip_range.gateway:
            raise ValueError(f"Cannot use gateway IP {ip_address}")

    device = Device(
        hostname=hostname,
        mac_address=mac_address,
        ip_address=ip_address,
        ip_range_id=ip_range_id,
        description=description,
        created_by=user_id,
        is_active=True
    )

    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def update_device(
    db: Session,
    device_id: int,
    **kwargs
) -> Optional[Device]:
    """
    Update a device

    Args:
        db: Database session
        device_id: Device ID
        **kwargs: Fields to update

    Returns:
        Updated device or None if not found

    Raises:
        ValueError: If validation fails or duplicates exist
    """
    device = get_device_by_id(db, device_id)
    if not device:
        return None

    # Normalize MAC address if provided
    if 'mac_address' in kwargs and kwargs['mac_address']:
        kwargs['mac_address'] = normalize_mac_address(kwargs['mac_address'])

        # Check for MAC duplicate (excluding current device)
        existing = get_device_by_mac(db, kwargs['mac_address'])
        if existing and existing.id != device_id:
            raise ValueError(f"Device with MAC address '{kwargs['mac_address']}' already exists")

    # Check for hostname duplicate (excluding current device)
    if 'hostname' in kwargs and kwargs['hostname']:
        existing = get_device_by_hostname(db, kwargs['hostname'])
        if existing and existing.id != device_id:
            raise ValueError(f"Device with hostname '{kwargs['hostname']}' already exists")

    # Check for IP duplicate (excluding current device)
    if 'ip_address' in kwargs and kwargs['ip_address']:
        existing = get_device_by_ip(db, kwargs['ip_address'])
        if existing and existing.id != device_id:
            raise ValueError(f"Device with IP address '{kwargs['ip_address']}' already exists")

        # Validate IP is in range if range is specified or being updated
        range_id = kwargs.get('ip_range_id', device.ip_range_id)
        if range_id:
            ip_range = db.query(IPRange).filter(IPRange.id == range_id).first()
            if ip_range:
                is_valid, error = validate_ip_in_range(
                    kwargs['ip_address'],
                    ip_range.network_address,
                    ip_range.cidr
                )
                if not is_valid:
                    raise ValueError(error)

    # Update fields
    for key, value in kwargs.items():
        if value is not None and hasattr(device, key):
            setattr(device, key, value)

    db.commit()
    db.refresh(device)
    return device


def delete_device(db: Session, device_id: int) -> bool:
    """
    Delete a device

    Args:
        db: Database session
        device_id: Device ID

    Returns:
        True if deleted, False if not found
    """
    device = get_device_by_id(db, device_id)
    if not device:
        return False

    db.delete(device)
    db.commit()
    return True


def suggest_available_ip_for_range(db: Session, range_id: int) -> Optional[str]:
    """
    Suggest next available IP address in a range

    Args:
        db: Database session
        range_id: IP range ID

    Returns:
        Suggested IP address or None if range full or not found
    """
    ip_range = db.query(IPRange).filter(IPRange.id == range_id).first()
    if not ip_range:
        return None

    # Get all assigned IPs in this range
    assigned_devices = db.query(Device.ip_address)\
        .filter(Device.ip_range_id == range_id)\
        .filter(Device.is_active == True)\
        .all()

    assigned_ips = set(device[0] for device in assigned_devices)

    # Suggest next available IP
    suggested = suggest_next_ip(
        ip_range.network_address,
        ip_range.cidr,
        assigned_ips,
        ip_range.gateway
    )

    return suggested
