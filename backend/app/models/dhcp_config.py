"""
DHCP Config model for configuration history
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class DHCPConfig(Base):
    """DHCP Configuration history model"""

    __tablename__ = "dhcp_configs"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(Integer, nullable=False, unique=True)
    config_content = Column(Text, nullable=False)  # Full configuration file content
    file_path = Column(String(255), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)  # Only one config can be active

    # Relationship
    generator = relationship("User")

    def __repr__(self):
        return f"<DHCPConfig(id={self.id}, version={self.version}, active={self.is_active})>"
