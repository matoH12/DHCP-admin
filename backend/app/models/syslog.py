"""
Syslog model for storing syslog messages
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from ..database import Base


class SyslogMessage(Base):
    """Syslog message model"""

    __tablename__ = "syslog_messages"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    facility = Column(String(50), nullable=True)
    severity = Column(String(20), nullable=True, index=True)
    hostname = Column(String(255), nullable=True, index=True)
    source_ip = Column(String(50), nullable=True, index=True)
    program = Column(String(100), nullable=True, index=True)
    message = Column(Text, nullable=False)
    raw_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<SyslogMessage(id={self.id}, timestamp='{self.timestamp}', severity='{self.severity}', program='{self.program}')>"
