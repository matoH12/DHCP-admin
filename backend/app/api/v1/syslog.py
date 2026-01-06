"""
Syslog API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import List, Optional
from datetime import datetime, timedelta
from ...database import get_db
from ...dependencies import get_current_user
from ...schemas.syslog import SyslogMessage
from ...models.syslog import SyslogMessage as SyslogModel
from ...models.user import User

router = APIRouter(prefix="/syslog", tags=["Syslog"])


@router.get("/", response_model=List[SyslogMessage])
def list_syslog_messages(
    skip: int = 0,
    limit: int = Query(100, le=1000),
    severity: Optional[str] = None,
    program: Optional[str] = None,
    hostname: Optional[str] = None,
    source_ip: Optional[str] = None,
    search: Optional[str] = None,
    hours: Optional[int] = Query(None, description="Filter logs from last N hours"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of syslog messages with optional filtering

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return (max 1000)
        severity: Filter by severity level
        program: Filter by program name
        hostname: Filter by hostname
        source_ip: Filter by source IP
        search: Search in message content
        hours: Show only logs from last N hours
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of syslog messages
    """
    query = db.query(SyslogModel)

    # Apply filters
    if severity:
        query = query.filter(SyslogModel.severity == severity)

    if program:
        query = query.filter(SyslogModel.program.ilike(f"%{program}%"))

    if hostname:
        query = query.filter(SyslogModel.hostname.ilike(f"%{hostname}%"))

    if source_ip:
        query = query.filter(SyslogModel.source_ip == source_ip)

    if search:
        query = query.filter(
            or_(
                SyslogModel.message.ilike(f"%{search}%"),
                SyslogModel.raw_message.ilike(f"%{search}%")
            )
        )

    if hours:
        since = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(SyslogModel.timestamp >= since)

    # Order by timestamp descending (newest first)
    query = query.order_by(desc(SyslogModel.timestamp))

    # Apply pagination
    messages = query.offset(skip).limit(limit).all()

    return messages


@router.get("/count", response_model=dict)
def get_syslog_count(
    severity: Optional[str] = None,
    program: Optional[str] = None,
    hostname: Optional[str] = None,
    source_ip: Optional[str] = None,
    search: Optional[str] = None,
    hours: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get count of syslog messages matching filters

    Returns:
        Dictionary with total count
    """
    query = db.query(SyslogModel)

    # Apply same filters as list endpoint
    if severity:
        query = query.filter(SyslogModel.severity == severity)
    if program:
        query = query.filter(SyslogModel.program.ilike(f"%{program}%"))
    if hostname:
        query = query.filter(SyslogModel.hostname.ilike(f"%{hostname}%"))
    if source_ip:
        query = query.filter(SyslogModel.source_ip == source_ip)
    if search:
        query = query.filter(
            or_(
                SyslogModel.message.ilike(f"%{search}%"),
                SyslogModel.raw_message.ilike(f"%{search}%")
            )
        )
    if hours:
        since = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(SyslogModel.timestamp >= since)

    count = query.count()
    return {"total": count}


@router.get("/stats", response_model=dict)
def get_syslog_stats(
    hours: int = Query(24, description="Stats for last N hours"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get syslog statistics

    Returns:
        Dictionary with statistics
    """
    since = datetime.utcnow() - timedelta(hours=hours)

    total = db.query(SyslogModel).filter(SyslogModel.timestamp >= since).count()

    # Count by severity
    severity_counts = {}
    for severity in ['emergency', 'alert', 'critical', 'error', 'warning', 'notice', 'info', 'debug']:
        count = db.query(SyslogModel).filter(
            SyslogModel.timestamp >= since,
            SyslogModel.severity == severity
        ).count()
        if count > 0:
            severity_counts[severity] = count

    # Top programs
    from sqlalchemy import func
    top_programs = db.query(
        SyslogModel.program,
        func.count(SyslogModel.id).label('count')
    ).filter(
        SyslogModel.timestamp >= since,
        SyslogModel.program.isnot(None)
    ).group_by(
        SyslogModel.program
    ).order_by(
        desc('count')
    ).limit(10).all()

    return {
        "total_messages": total,
        "time_range_hours": hours,
        "severity_counts": severity_counts,
        "top_programs": [{"program": p[0], "count": p[1]} for p in top_programs]
    }


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_syslog_message(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a syslog message (Admin only)

    Args:
        log_id: Syslog message ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If log not found or user not admin
    """
    if current_user.role != 'ADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete logs"
        )

    log_entry = db.query(SyslogModel).filter(SyslogModel.id == log_id).first()
    if not log_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log entry with ID {log_id} not found"
        )

    db.delete(log_entry)
    db.commit()
    return None


@router.delete("/bulk", status_code=status.HTTP_204_NO_CONTENT)
def delete_old_logs(
    days: int = Query(..., description="Delete logs older than N days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete old syslog messages (Admin only)

    Args:
        days: Delete logs older than this many days
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If user not admin
    """
    if current_user.role != 'ADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete logs"
        )

    cutoff = datetime.utcnow() - timedelta(days=days)
    deleted = db.query(SyslogModel).filter(SyslogModel.timestamp < cutoff).delete()
    db.commit()

    return {"deleted": deleted}
