"""
IP Range API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...database import get_db
from ...dependencies import get_current_user
from ...schemas.ip_range import IPRange, IPRangeCreate, IPRangeUpdate, IPRangeWithStats
from ...services import ip_range_service
from ...models.user import User

router = APIRouter(prefix="/ranges", tags=["IP Ranges"])


@router.get("/", response_model=List[IPRange])
def list_ip_ranges(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all IP ranges

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of IP ranges
    """
    ranges = ip_range_service.get_ip_ranges(db, skip=skip, limit=limit)
    return ranges


@router.get("/{range_id}", response_model=IPRange)
def get_ip_range(
    range_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific IP range by ID

    Args:
        range_id: IP range ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        IP range details

    Raises:
        HTTPException: If range not found
    """
    ip_range = ip_range_service.get_ip_range_by_id(db, range_id)
    if not ip_range:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IP range with ID {range_id} not found"
        )
    return ip_range


@router.post("/", response_model=IPRange, status_code=status.HTTP_201_CREATED)
def create_ip_range(
    range_data: IPRangeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new IP range

    Args:
        range_data: IP range creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created IP range

    Raises:
        HTTPException: If range with same name exists or validation fails
    """
    # Check if range with same name exists
    existing = ip_range_service.get_ip_range_by_name(db, range_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"IP range with name '{range_data.name}' already exists"
        )

    try:
        ip_range = ip_range_service.create_ip_range(
            db,
            name=range_data.name,
            network_address=range_data.network_address,
            cidr=range_data.cidr,
            gateway=range_data.gateway,
            dns_servers=range_data.dns_servers,
            domain_name=range_data.domain_name,
            description=range_data.description,
            pool_start=range_data.pool_start,
            pool_end=range_data.pool_end
        )
        return ip_range
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{range_id}", response_model=IPRange)
def update_ip_range(
    range_id: int,
    range_data: IPRangeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an IP range

    Args:
        range_id: IP range ID
        range_data: IP range update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated IP range

    Raises:
        HTTPException: If range not found or validation fails
    """
    # Check if range with same name exists (if name is being changed)
    if range_data.name:
        existing = ip_range_service.get_ip_range_by_name(db, range_data.name)
        if existing and existing.id != range_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"IP range with name '{range_data.name}' already exists"
            )

    update_data = range_data.model_dump(exclude_unset=True)
    ip_range = ip_range_service.update_ip_range(db, range_id, **update_data)

    if not ip_range:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IP range with ID {range_id} not found"
        )

    return ip_range


@router.delete("/{range_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ip_range(
    range_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an IP range

    Args:
        range_id: IP range ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If range not found
    """
    deleted = ip_range_service.delete_ip_range(db, range_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IP range with ID {range_id} not found"
        )
    return None


@router.get("/{range_id}/stats", response_model=dict)
def get_range_statistics(
    range_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get usage statistics for an IP range

    Args:
        range_id: IP range ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Statistics dictionary with usage information

    Raises:
        HTTPException: If range not found
    """
    stats = ip_range_service.get_ip_range_statistics(db, range_id)
    if stats is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IP range with ID {range_id} not found"
        )
    return stats


@router.get("/{range_id}/available-ips", response_model=List[str])
def get_available_ips(
    range_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available IP addresses in a range

    Args:
        range_id: IP range ID
        limit: Maximum number of IPs to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of available IP addresses

    Raises:
        HTTPException: If range not found
    """
    available_ips = ip_range_service.get_available_ips_in_range(db, range_id)
    if available_ips is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IP range with ID {range_id} not found"
        )
    return available_ips[:limit]
