"""
Device History Service

Manages device activity tracking and historical analytics.
Records DHCP events for timeline charts and activity analysis.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

from ..models.device_history import DeviceHistory
from ..models.device import Device

logger = logging.getLogger(__name__)


def record_device_activity(
    db: Session,
    device_id: int,
    event_type: str,
    timestamp: Optional[datetime] = None,
    ip_address: Optional[str] = None,
    mac_address: Optional[str] = None
) -> DeviceHistory:
    """
    Record device activity event from DHCP logs.

    Called when DHCP ACK/REQUEST is detected in syslog.
    Creates a history record for analytics and timeline tracking.

    Args:
        db: Database session
        device_id: Device ID
        event_type: DHCP event type (ACK, REQUEST, etc.)
        timestamp: Event timestamp (defaults to now)
        ip_address: IP address at time of event (fetched from device if not provided)
        mac_address: MAC address (fetched from device if not provided)

    Returns:
        Created DeviceHistory record
    """
    try:
        # Fetch device if IP/MAC not provided
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            logger.error(f"Device {device_id} not found for activity recording")
            raise ValueError(f"Device {device_id} not found")

        # Use provided values or fetch from device
        ip = ip_address or device.ip_address
        mac = mac_address or device.mac_address
        ts = timestamp or datetime.utcnow()

        # Create history record
        history = DeviceHistory(
            device_id=device_id,
            timestamp=ts,
            ip_address=ip,
            mac_address=mac,
            event_type=event_type,
            is_active=device.is_active
        )

        db.add(history)
        db.commit()
        db.refresh(history)

        logger.debug(f"Recorded activity for device {device_id}: {event_type} at {ts}")
        return history

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to record device activity: {e}")
        raise


def get_activity_timeline(
    db: Session,
    days: int = 7
) -> Tuple[List[Dict], datetime, datetime]:
    """
    Get daily aggregated device activity counts for timeline charts.

    Uses server-side aggregation with func.date() for performance.
    Returns data suitable for Recharts AreaChart/LineChart.

    Args:
        db: Database session
        days: Number of days to look back (1-90)

    Returns:
        Tuple of:
        - List of dicts: [{ date: "2026-01-01", active_devices: 15, total_events: 45 }, ...]
        - period_start: Start of period
        - period_end: End of period
    """
    if days < 1 or days > 90:
        raise ValueError("Days must be between 1 and 90")

    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=days)

    try:
        # Aggregate by date: count distinct devices and total events
        results = db.query(
            func.date(DeviceHistory.timestamp).label('date'),
            func.count(func.distinct(DeviceHistory.device_id)).label('active_devices'),
            func.count(DeviceHistory.id).label('total_events')
        ).filter(
            DeviceHistory.timestamp >= period_start,
            DeviceHistory.timestamp <= period_end
        ).group_by(
            func.date(DeviceHistory.timestamp)
        ).order_by('date').all()

        # Convert to list of dicts
        timeline_data = [
            {
                'date': str(row.date),
                'active_devices': row.active_devices,
                'total_events': row.total_events
            }
            for row in results
        ]

        logger.info(f"Retrieved activity timeline for {days} days: {len(timeline_data)} data points")
        return timeline_data, period_start, period_end

    except Exception as e:
        logger.error(f"Failed to get activity timeline: {e}")
        raise


def get_device_activity_history(
    db: Session,
    device_id: int,
    limit: int = 100
) -> List[DeviceHistory]:
    """
    Get activity history for a specific device.

    Args:
        db: Database session
        device_id: Device ID
        limit: Maximum number of records to return

    Returns:
        List of DeviceHistory records, ordered by timestamp descending
    """
    try:
        history = db.query(DeviceHistory).filter(
            DeviceHistory.device_id == device_id
        ).order_by(
            desc(DeviceHistory.timestamp)
        ).limit(limit).all()

        logger.debug(f"Retrieved {len(history)} history records for device {device_id}")
        return history

    except Exception as e:
        logger.error(f"Failed to get device history: {e}")
        raise


def get_top_active_devices(
    db: Session,
    limit: int = 10,
    days: int = 7
) -> List[Dict]:
    """
    Get most active devices based on recent activity count.

    Joins Device + DeviceHistory + IPRange for complete device info.
    Ranks by number of activity events in the specified period.

    Args:
        db: Database session
        limit: Number of devices to return (5-50)
        days: Period to analyze (1-30)

    Returns:
        List of dicts with device info and activity count:
        [{
            device_id, hostname, ip_address, mac_address,
            activity_count, last_seen, range_name
        }, ...]
    """
    if limit < 5 or limit > 50:
        raise ValueError("Limit must be between 5 and 50")
    if days < 1 or days > 30:
        raise ValueError("Days must be between 1 and 30")

    period_start = datetime.utcnow() - timedelta(days=days)

    try:
        # Import here to avoid circular dependency
        from ..models.ip_range import IPRange

        # Subquery: count activities per device
        activity_counts = db.query(
            DeviceHistory.device_id,
            func.count(DeviceHistory.id).label('activity_count'),
            func.max(DeviceHistory.timestamp).label('last_activity')
        ).filter(
            DeviceHistory.timestamp >= period_start
        ).group_by(
            DeviceHistory.device_id
        ).subquery()

        # Join with devices and ranges
        results = db.query(
            Device.id.label('device_id'),
            Device.hostname,
            Device.ip_address,
            Device.mac_address,
            Device.last_seen,
            activity_counts.c.activity_count,
            IPRange.name.label('range_name')
        ).join(
            activity_counts,
            Device.id == activity_counts.c.device_id
        ).outerjoin(
            IPRange,
            Device.ip_range_id == IPRange.id
        ).order_by(
            desc(activity_counts.c.activity_count)
        ).limit(limit).all()

        # Convert to list of dicts
        top_devices = [
            {
                'device_id': row.device_id,
                'hostname': row.hostname,
                'ip_address': row.ip_address,
                'mac_address': row.mac_address,
                'activity_count': row.activity_count,
                'last_seen': row.last_seen,
                'range_name': row.range_name
            }
            for row in results
        ]

        logger.info(f"Retrieved top {len(top_devices)} active devices for {days} days")
        return top_devices

    except Exception as e:
        logger.error(f"Failed to get top active devices: {e}")
        raise


def cleanup_old_history(
    db: Session,
    days: int = 90
) -> int:
    """
    Delete device history records older than specified retention period.

    Should be run daily via scheduled job/cron.
    Default retention: 90 days.

    Args:
        db: Database session
        days: Retention period in days

    Returns:
        Number of records deleted
    """
    if days < 7:
        raise ValueError("Retention period must be at least 7 days")

    cutoff = datetime.utcnow() - timedelta(days=days)

    try:
        deleted = db.query(DeviceHistory).filter(
            DeviceHistory.timestamp < cutoff
        ).delete()

        db.commit()

        logger.info(f"Cleaned up {deleted} device history records older than {days} days")
        return deleted

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to cleanup old history: {e}")
        raise


def get_activity_summary(db: Session, device_id: int, days: int = 7) -> Dict:
    """
    Get activity summary for a device over specified period.

    Useful for device detail pages.

    Args:
        db: Database session
        device_id: Device ID
        days: Period to analyze

    Returns:
        Dict with activity metrics:
        {
            'total_events': int,
            'first_seen': datetime,
            'last_seen': datetime,
            'days_active': int,
            'avg_events_per_day': float
        }
    """
    period_start = datetime.utcnow() - timedelta(days=days)

    try:
        # Get activity stats
        stats = db.query(
            func.count(DeviceHistory.id).label('total_events'),
            func.min(DeviceHistory.timestamp).label('first_seen'),
            func.max(DeviceHistory.timestamp).label('last_seen'),
            func.count(func.distinct(func.date(DeviceHistory.timestamp))).label('days_active')
        ).filter(
            DeviceHistory.device_id == device_id,
            DeviceHistory.timestamp >= period_start
        ).first()

        if not stats or stats.total_events == 0:
            return {
                'total_events': 0,
                'first_seen': None,
                'last_seen': None,
                'days_active': 0,
                'avg_events_per_day': 0.0
            }

        avg_events = stats.total_events / stats.days_active if stats.days_active > 0 else 0.0

        return {
            'total_events': stats.total_events,
            'first_seen': stats.first_seen,
            'last_seen': stats.last_seen,
            'days_active': stats.days_active,
            'avg_events_per_day': round(avg_events, 2)
        }

    except Exception as e:
        logger.error(f"Failed to get activity summary: {e}")
        raise
