"""
Device model for DHCP host reservations
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Device(Base):
    """Device model for DHCP static host reservations"""

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String(63), unique=True, index=True, nullable=False)  # DNS label limit
    mac_address = Column(String(17), unique=True, index=True, nullable=False)  # XX:XX:XX:XX:XX:XX
    ip_address = Column(String(15), unique=True, index=True, nullable=False)  # IPv4 address
    ip_range_id = Column(Integer, ForeignKey("ip_ranges.id"), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    ip_range = relationship("IPRange", back_populates="devices")
    creator = relationship("User")

    def __repr__(self):
        return f"<Device(id={self.id}, hostname='{self.hostname}', mac='{self.mac_address}', ip='{self.ip_address}')>"
