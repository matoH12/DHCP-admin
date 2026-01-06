"""
Device History Model

Tracks device activity over time for analytics and historical reporting.
Records are created when DHCP events (ACK, REQUEST) are detected in syslog.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class DeviceHistory(Base):
    """
    Device activity history for tracking DHCP events and device presence over time.

    Used for:
    - Activity timeline charts (devices active per day)
    - Top active devices ranking
    - Historical analysis of device behavior

    Retention: 90 days (configurable via cleanup job)
    """
    __tablename__ = "device_history"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, server_default=func.now())
    ip_address = Column(String(15), nullable=False)  # IP at time of event
    mac_address = Column(String(17), nullable=False)  # Denormalized for faster queries
    event_type = Column(String(20), nullable=True)  # DHCP event: ACK, REQUEST, etc.
    is_active = Column(Boolean, default=True, nullable=False)  # Device active status at time of event

    # Relationships
    device = relationship("Device", backref="history")

    # Composite indexes for optimized query performance
    __table_args__ = (
        Index('idx_device_history_device_timestamp', 'device_id', 'timestamp'),
        Index('idx_device_history_timestamp', 'timestamp'),
    )

    def __repr__(self):
        return f"<DeviceHistory(device_id={self.device_id}, event={self.event_type}, timestamp={self.timestamp})>"
