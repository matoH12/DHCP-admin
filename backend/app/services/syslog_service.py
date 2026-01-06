"""
Syslog service for querying DHCP activity
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_
from datetime import datetime
from typing import Optional, Dict
from ..models.syslog import SyslogMessage
import re


def get_device_last_seen(
    db: Session,
    mac_address: str,
    ip_address: str
) -> Optional[datetime]:
    """
    Get the last time a device was seen in DHCP logs.
    Searches for DHCP messages containing the device's MAC or IP address.

    Args:
        db: Database session
        mac_address: Device MAC address (format: XX:XX:XX:XX:XX:XX)
        ip_address: Device IP address

    Returns:
        datetime of last activity, or None if never seen
    """
    # Normalize MAC address to lowercase and remove colons for flexible matching
    mac_normalized = mac_address.lower().replace(':', '')
    mac_with_colons = mac_address.lower()
    mac_with_dashes = mac_address.lower().replace(':', '-')

    # Search for DHCP-related messages containing this device
    # DHCP messages typically contain:
    # - "DHCPACK on 192.168.1.10 to aa:bb:cc:dd:ee:ff"
    # - "DHCPREQUEST for 192.168.1.10 from aa:bb:cc:dd:ee:ff"
    # - "DHCPDISCOVER from aa:bb:cc:dd:ee:ff"
    # - "DHCPRELEASE of 192.168.1.10 from aa:bb:cc:dd:ee:ff"

    query = db.query(SyslogMessage).filter(
        and_(
            # Filter for DHCP-related programs
            or_(
                SyslogMessage.program.ilike('%dhcp%'),
                SyslogMessage.message.ilike('%dhcp%')
            ),
            # Filter for messages containing the MAC or IP
            or_(
                SyslogMessage.message.ilike(f'%{mac_with_colons}%'),
                SyslogMessage.message.ilike(f'%{mac_with_dashes}%'),
                SyslogMessage.message.ilike(f'%{ip_address}%')
            )
        )
    ).order_by(desc(SyslogMessage.timestamp)).first()

    if query:
        return query.timestamp

    return None


def get_devices_last_seen(
    db: Session,
    devices: list
) -> Dict[int, Optional[datetime]]:
    """
    Get last seen timestamps for multiple devices at once (bulk operation).

    Args:
        db: Database session
        devices: List of device objects with id, mac_address, ip_address

    Returns:
        Dictionary mapping device_id to last_seen timestamp
    """
    result = {}

    for device in devices:
        last_seen = get_device_last_seen(
            db,
            device.mac_address,
            device.ip_address
        )
        result[device.id] = last_seen

    return result


def parse_dhcp_event_type(message: str) -> Optional[str]:
    """
    Parse DHCP event type from log message.

    Returns:
        Event type: DISCOVER, OFFER, REQUEST, ACK, NAK, RELEASE, INFORM, DECLINE
    """
    message_upper = message.upper()

    if 'DHCPDISCOVER' in message_upper:
        return 'DISCOVER'
    elif 'DHCPOFFER' in message_upper:
        return 'OFFER'
    elif 'DHCPREQUEST' in message_upper:
        return 'REQUEST'
    elif 'DHCPACK' in message_upper:
        return 'ACK'
    elif 'DHCPNAK' in message_upper:
        return 'NAK'
    elif 'DHCPRELEASE' in message_upper:
        return 'RELEASE'
    elif 'DHCPINFORM' in message_upper:
        return 'INFORM'
    elif 'DHCPDECLINE' in message_upper:
        return 'DECLINE'

    return None


def get_device_dhcp_activity(
    db: Session,
    mac_address: str,
    ip_address: str,
    limit: int = 10
) -> list:
    """
    Get recent DHCP activity for a device.

    Args:
        db: Database session
        mac_address: Device MAC address
        ip_address: Device IP address
        limit: Maximum number of events to return

    Returns:
        List of DHCP activity events with timestamp, event_type, and message
    """
    mac_with_colons = mac_address.lower()
    mac_with_dashes = mac_address.lower().replace(':', '-')

    messages = db.query(SyslogMessage).filter(
        and_(
            or_(
                SyslogMessage.program.ilike('%dhcp%'),
                SyslogMessage.message.ilike('%dhcp%')
            ),
            or_(
                SyslogMessage.message.ilike(f'%{mac_with_colons}%'),
                SyslogMessage.message.ilike(f'%{mac_with_dashes}%'),
                SyslogMessage.message.ilike(f'%{ip_address}%')
            )
        )
    ).order_by(desc(SyslogMessage.timestamp)).limit(limit).all()

    activity = []
    for msg in messages:
        activity.append({
            'timestamp': msg.timestamp,
            'event_type': parse_dhcp_event_type(msg.message),
            'message': msg.message,
            'severity': msg.severity
        })

    return activity
