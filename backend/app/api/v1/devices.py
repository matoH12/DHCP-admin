"""
Device API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...database import get_db
from ...dependencies import get_current_user
from ...schemas.device import Device, DeviceCreate, DeviceUpdate
from ...services import device_service
from ...models.user import User

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get("/", response_model=List[Device])
def list_devices(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search in hostname, MAC, IP, description"),
    ip_range_id: Optional[int] = Query(None, description="Filter by IP range ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all devices with optional search and filters

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        search: Search query (searches hostname, MAC, IP, description)
        ip_range_id: Filter by IP range
        is_active: Filter by active status
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of devices with last_seen from DHCP logs
    """
    devices = device_service.get_devices(
        db,
        skip=skip,
        limit=limit,
        search=search,
        ip_range_id=ip_range_id,
        is_active=is_active
    )

    # Return devices with last_seen from database
    # (updated automatically by log monitor from DHCP logs)
    return devices


@router.get("/{device_id}", response_model=Device)
def get_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific device by ID

    Args:
        device_id: Device ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Device details with last_seen from DHCP logs

    Raises:
        HTTPException: If device not found
    """
    device = device_service.get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )

    # Return device with last_seen from database
    # (updated automatically by log monitor from DHCP logs)
    return device


@router.post("/", response_model=Device, status_code=status.HTTP_201_CREATED)
def create_device(
    device_data: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new device

    Args:
        device_data: Device creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created device

    Raises:
        HTTPException: If validation fails or duplicates exist
    """
    try:
        device = device_service.create_device(
            db,
            hostname=device_data.hostname,
            mac_address=device_data.mac_address,
            ip_address=device_data.ip_address,
            ip_range_id=device_data.ip_range_id,
            description=device_data.description,
            user_id=current_user.id
        )
        return device
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{device_id}", response_model=Device)
def update_device(
    device_id: int,
    device_data: DeviceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a device

    Args:
        device_id: Device ID
        device_data: Device update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated device

    Raises:
        HTTPException: If device not found or validation fails
    """
    try:
        update_data = device_data.model_dump(exclude_unset=True)
        device = device_service.update_device(db, device_id, **update_data)

        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID {device_id} not found"
            )

        return device
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a device

    Args:
        device_id: Device ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If device not found
    """
    deleted = device_service.delete_device(db, device_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    return None


@router.get("/suggest-ip/{range_id}", response_model=dict)
def suggest_ip_for_range(
    range_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Suggest next available IP address in a range

    Args:
        range_id: IP range ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Dictionary with suggested IP address

    Raises:
        HTTPException: If range not found or no IPs available
    """
    suggested_ip = device_service.suggest_available_ip_for_range(db, range_id)

    if suggested_ip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No available IPs in range {range_id} or range not found"
        )

    return {"suggested_ip": suggested_ip}
