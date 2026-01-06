"""
IP Range model for subnet management
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class IPRange(Base):
    """IP Range/Subnet model for defining network ranges"""

    __tablename__ = "ip_ranges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    network_address = Column(String(15), nullable=False)  # e.g., "192.168.1.0"
    cidr = Column(Integer, nullable=False)  # e.g., 24 for /24
    gateway = Column(String(15), nullable=True)  # e.g., "192.168.1.1"
    dns_servers = Column(Text, nullable=True)  # JSON array stored as text
    domain_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    # DHCP Pool for dynamic IP allocation
    pool_start = Column(String(15), nullable=True)  # e.g., "192.168.1.100"
    pool_end = Column(String(15), nullable=True)    # e.g., "192.168.1.200"

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship to devices
    devices = relationship("Device", back_populates="ip_range", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<IPRange(id={self.id}, name='{self.name}', network='{self.network_address}/{self.cidr}')>"
