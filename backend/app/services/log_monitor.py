"""
Log file monitor for tracking device activity from DHCP logs
"""
import threading
import time
import os
from datetime import datetime
from ..database import SessionLocal
from .syslog_server import extract_mac_from_dhcp_log, update_device_last_seen

DHCP_LOG_FILE = "/var/log/dhcp/dhcpd.log"
CHECK_INTERVAL = 10  # seconds


class LogMonitor:
    """Monitor DHCP log file for new entries and update device last_seen"""

    def __init__(self):
        self.running = False
        self.thread = None
        self.last_position = 0
        self.last_inode = None

    def start(self):
        """Start monitoring log file in background thread"""
        print(f"[LOG MONITOR] start() called, running={self.running}")
        if self.running:
            print(f"[LOG MONITOR] Already running, skipping")
            return

        if not os.path.exists(DHCP_LOG_FILE):
            print(f"[LOG MONITOR] Warning: Log file {DHCP_LOG_FILE} does not exist yet")

        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print(f"✓ Log monitor started (checking every {CHECK_INTERVAL}s)")
        print(f"[LOG MONITOR] Thread started: {self.thread.is_alive()}, daemon={self.thread.daemon}")

    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

    def _monitor_loop(self):
        """Main monitoring loop"""
        print(f"[LOG MONITOR] Monitor loop started, will check every {CHECK_INTERVAL}s")
        while self.running:
            try:
                self._check_log_file()
            except Exception as e:
                print(f"[LOG MONITOR ERROR] {e}")
                import traceback
                traceback.print_exc()

            time.sleep(CHECK_INTERVAL)

    def _check_log_file(self):
        """Check log file for new entries"""
        if not os.path.exists(DHCP_LOG_FILE):
            return

        try:
            # Check if file was rotated (inode changed)
            current_inode = os.stat(DHCP_LOG_FILE).st_ino
            if self.last_inode and current_inode != self.last_inode:
                print("[LOG MONITOR] Log file rotated, resetting position")
                self.last_position = 0
            self.last_inode = current_inode

            # Read new lines
            with open(DHCP_LOG_FILE, 'r') as f:
                f.seek(self.last_position)
                new_lines = f.readlines()
                self.last_position = f.tell()

            if not new_lines:
                return

            print(f"[LOG MONITOR] Processing {len(new_lines)} new log lines")
            # Process new lines
            db = SessionLocal()
            try:
                for line in new_lines:
                    self._process_log_line(line.strip(), db)
            finally:
                db.close()

        except Exception as e:
            print(f"[LOG MONITOR ERROR] Failed to read log file: {e}")

    def _process_log_line(self, line: str, db):
        """Process a single log line and update device if DHCP activity detected"""
        if not line:
            return

        # Check if it's a DHCP log line (contains dhcpd)
        if 'dhcpd' not in line.lower():
            return

        # Look for DHCP activity keywords
        dhcp_keywords = ['DHCPREQUEST', 'DHCPACK', 'DHCPDISCOVER', 'DHCPOFFER']
        if not any(keyword in line for keyword in dhcp_keywords):
            return

        print(f"[LOG MONITOR] Found DHCP activity: {line[:100]}")

        # Extract MAC address
        mac_address = extract_mac_from_dhcp_log(line)
        if mac_address:
            print(f"[LOG MONITOR] Extracted MAC: {mac_address}")
            result = update_device_last_seen(db, mac_address)
            if not result:
                print(f"[LOG MONITOR] Device with MAC {mac_address} not found in database")
        else:
            print(f"[LOG MONITOR] Could not extract MAC from line")


# Global monitor instance
log_monitor = LogMonitor()


def start_log_monitor():
    """Start the log monitor"""
    log_monitor.start()


def stop_log_monitor():
    """Stop the log monitor"""
    log_monitor.stop()
