"""
Settings service
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict
from ..models.settings import Settings


def get_setting(db: Session, key: str) -> Optional[str]:
    """Get a setting value by key"""
    setting = db.query(Settings).filter(Settings.key == key).first()
    return setting.value if setting else None


def get_all_settings(db: Session) -> Dict[str, str]:
    """Get all settings as a dictionary"""
    settings = db.query(Settings).all()
    return {s.key: s.value for s in settings}


def update_setting(db: Session, key: str, value: str) -> bool:
    """Update a setting value"""
    setting = db.query(Settings).filter(Settings.key == key).first()
    if setting:
        setting.value = value
        db.commit()
        return True
    return False


def get_syslog_retention_days(db: Session) -> int:
    """Get the syslog retention period in days"""
    value = get_setting(db, 'syslog_retention_days')
    try:
        return int(value) if value else 180
    except ValueError:
        return 180


def is_syslog_cleanup_enabled(db: Session) -> bool:
    """Check if automatic syslog cleanup is enabled"""
    value = get_setting(db, 'syslog_cleanup_enabled')
    return value.lower() == 'true' if value else True


def get_syslog_cleanup_hour(db: Session) -> int:
    """Get the hour when cleanup should run (0-23)"""
    value = get_setting(db, 'syslog_cleanup_hour')
    try:
        hour = int(value) if value else 2
        return max(0, min(23, hour))  # Ensure it's between 0-23
    except ValueError:
        return 2
