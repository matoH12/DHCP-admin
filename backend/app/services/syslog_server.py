"""
Syslog server for receiving and storing syslog messages
"""
import socketserver
import re
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.syslog import SyslogMessage
from ..models.device import Device
from ..database import SessionLocal
import threading


# Syslog severity levels
SEVERITY_MAP = {
    0: 'emergency',
    1: 'alert',
    2: 'critical',
    3: 'error',
    4: 'warning',
    5: 'notice',
    6: 'info',
    7: 'debug'
}

# Syslog facility codes
FACILITY_MAP = {
    0: 'kernel',
    1: 'user',
    2: 'mail',
    3: 'daemon',
    4: 'auth',
    5: 'syslog',
    6: 'lpr',
    7: 'news',
    8: 'uucp',
    9: 'cron',
    10: 'authpriv',
    11: 'ftp',
    16: 'local0',
    17: 'local1',
    18: 'local2',
    19: 'local3',
    20: 'local4',
    21: 'local5',
    22: 'local6',
    23: 'local7'
}


def parse_syslog_message(data: bytes, source_ip: str) -> dict:
    """
    Parse a syslog message (RFC 3164 format)

    Format: <PRI>TIMESTAMP HOSTNAME PROGRAM[PID]: MESSAGE
    Example: <34>Oct 11 22:14:15 mymachine su: 'su root' failed for user on /dev/pts/8
    """
    try:
        message_str = data.decode('utf-8', errors='ignore').strip()
    except Exception:
        message_str = str(data)

    result = {
        'raw_message': message_str,
        'source_ip': source_ip,
        'timestamp': datetime.utcnow(),
        'facility': None,
        'severity': None,
        'hostname': None,
        'program': None,
        'message': message_str
    }

    # Parse priority
    pri_match = re.match(r'^<(\d+)>', message_str)
    if pri_match:
        pri = int(pri_match.group(1))
        facility = pri // 8
        severity = pri % 8

        result['facility'] = FACILITY_MAP.get(facility, f'unknown({facility})')
        result['severity'] = SEVERITY_MAP.get(severity, f'unknown({severity})')

        # Remove priority from message
        message_str = message_str[pri_match.end():]

    # Try to parse timestamp (various formats)
    # RFC 3164: Oct 11 22:14:15
    timestamp_patterns = [
        r'^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+',
        r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+',
    ]

    for pattern in timestamp_patterns:
        ts_match = re.match(pattern, message_str)
        if ts_match:
            try:
                # For now, just use current time; parsing various formats is complex
                result['timestamp'] = datetime.utcnow()
            except:
                pass
            message_str = message_str[ts_match.end():]
            break

    # Parse hostname and program
    # Format: hostname program[pid]: message
    parts = message_str.split(None, 1)
    if len(parts) >= 1:
        hostname_program = parts[0]
        remaining = parts[1] if len(parts) > 1 else ''

        # Check if it looks like hostname program:
        if ' ' in remaining or ':' in hostname_program:
            # First part is likely hostname
            result['hostname'] = hostname_program

            # Try to find program
            prog_match = re.match(r'^(\S+?)(?:\[(\d+)\])?:\s*(.*)$', remaining)
            if prog_match:
                result['program'] = prog_match.group(1)
                result['message'] = prog_match.group(3)
            else:
                result['message'] = remaining
        else:
            # Might be program only
            prog_match = re.match(r'^(\S+?)(?:\[(\d+)\])?:\s*(.*)$', message_str)
            if prog_match:
                result['program'] = prog_match.group(1)
                result['message'] = prog_match.group(3)

    return result


def extract_mac_from_dhcp_log(message: str) -> str | None:
    """
    Extract MAC address from DHCP log messages

    Examples:
    - DHCPREQUEST for 192.168.33.3 from 00:50:56:ae:25:0a via ens35
    - DHCPACK on 192.168.33.3 to 00:50:56:ae:25:0a via ens35
    - DHCPDISCOVER from 00:11:22:33:44:55 via eth0
    """
    # Pattern for MAC address (XX:XX:XX:XX:XX:XX)
    mac_pattern = r'\b([0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2})\b'

    match = re.search(mac_pattern, message)
    if match:
        # Normalize to uppercase with colons
        mac = match.group(1).upper()
        return mac

    return None


def update_device_last_seen(db: Session, mac_address: str, event_type: str = 'ACK'):
    """
    Update last_seen timestamp for device with given MAC address
    and record activity in device history for analytics

    Args:
        db: Database session
        mac_address: Device MAC address
        event_type: DHCP event type (ACK, REQUEST, etc.)
    """
    try:
        device = db.query(Device).filter(Device.mac_address == mac_address).first()
        if device:
            device.last_seen = datetime.utcnow()
            db.commit()
            print(f"[DHCP] Updated last_seen for device {device.hostname} ({mac_address})")

            # Record activity in device_history for analytics
            try:
                from .device_history_service import record_device_activity
                record_device_activity(
                    db=db,
                    device_id=device.id,
                    event_type=event_type
                )
                print(f"[DHCP] Recorded {event_type} activity for device {device.hostname}")
            except Exception as history_error:
                print(f"[DHCP WARNING] Failed to record device history: {history_error}")
                # Don't fail the whole operation if history recording fails

            return True
        return False
    except Exception as e:
        print(f"[DHCP ERROR] Failed to update last_seen for {mac_address}: {e}")
        db.rollback()
        return False


class SyslogUDPHandler(socketserver.BaseRequestHandler):
    """Handler for UDP syslog messages"""

    def handle(self):
        data = self.request[0]
        source_ip = self.client_address[0]

        # Parse the syslog message
        parsed = parse_syslog_message(data, source_ip)

        # Store in database
        db = SessionLocal()
        try:
            syslog_entry = SyslogMessage(
                timestamp=parsed['timestamp'],
                facility=parsed['facility'],
                severity=parsed['severity'],
                hostname=parsed['hostname'],
                source_ip=parsed['source_ip'],
                program=parsed['program'],
                message=parsed['message'],
                raw_message=parsed['raw_message']
            )
            db.add(syslog_entry)
            db.commit()
            print(f"[SYSLOG] Received from {source_ip}: {parsed['message'][:100]}")
            print(f"[SYSLOG DEBUG] program='{parsed['program']}', facility='{parsed['facility']}', severity='{parsed['severity']}'")

            # Extract MAC address from DHCP logs and update device last_seen
            if parsed['program'] == 'dhcpd' and parsed['message']:
                print(f"[SYSLOG DEBUG] Found dhcpd message, checking for MAC...")
                mac_address = extract_mac_from_dhcp_log(parsed['message'])
                if mac_address:
                    print(f"[SYSLOG DEBUG] Extracted MAC: {mac_address}, updating device...")
                    update_device_last_seen(db, mac_address)

        except Exception as e:
            print(f"[SYSLOG ERROR] Failed to store message: {e}")
            db.rollback()
        finally:
            db.close()


def start_syslog_server(host='0.0.0.0', port=514):
    """Start the syslog UDP server"""
    server = socketserver.UDPServer((host, port), SyslogUDPHandler)
    print(f"✓ Syslog server listening on {host}:{port}")
    server.serve_forever()


def start_syslog_server_thread(host='0.0.0.0', port=514):
    """Start syslog server in a background thread"""
    thread = threading.Thread(
        target=start_syslog_server,
        args=(host, port),
        daemon=True
    )
    thread.start()
    return thread
