"""
Settings service for managing application settings
"""
from sqlalchemy.orm import Session
from datetime import datetime
from ..models.settings import Settings


def create_default_settings_if_not_exists(db: Session) -> bool:
    """
    Create default settings if they don't exist

    Args:
        db: Database session

    Returns:
        True if settings were created, False if they already existed
    """
    # Check if settings already exist
    existing_count = db.query(Settings).count()
    if existing_count > 0:
        return False

    # Default settings
    default_settings = [
        {
            'key': 'syslog_retention_days',
            'value': '30',
            'description': 'Number of days to keep DHCP syslog messages before automatic cleanup'
        },
        {
            'key': 'syslog_cleanup_enabled',
            'value': 'true',
            'description': 'Enable automatic cleanup of old syslog messages'
        },
        {
            'key': 'syslog_cleanup_hour',
            'value': '2',
            'description': 'Hour of day (0-23) when automatic cleanup runs'
        },
        {
            'key': 'pending_changes',
            'value': 'false',
            'description': 'Indicates whether DHCP configuration has pending changes'
        }
    ]

    # Create settings
    for setting_data in default_settings:
        setting = Settings(
            key=setting_data['key'],
            value=setting_data['value'],
            description=setting_data['description'],
            updated_at=datetime.utcnow()
        )
        db.add(setting)

    db.commit()
    print(f"✅ Created {len(default_settings)} default settings")
    return True


def get_setting_value(db: Session, key: str, default: str = None) -> str | None:
    """Get setting value by key"""
    setting = db.query(Settings).filter(Settings.key == key).first()
    if setting:
        return setting.value
    return default


def get_setting_as_int(db: Session, key: str, default: int = None) -> int | None:
    """Get setting value as integer"""
    value = get_setting_value(db, key)
    if value:
        try:
            return int(value)
        except ValueError:
            return default
    return default


def get_setting_as_bool(db: Session, key: str, default: bool = None) -> bool | None:
    """Get setting value as boolean"""
    value = get_setting_value(db, key)
    if value:
        return value.lower() in ['true', '1', 'yes', 'on']
    return default


# Convenience functions for specific settings used by cleanup_scheduler
def get_syslog_retention_days(db: Session) -> int:
    """Get syslog retention days setting"""
    return get_setting_as_int(db, 'syslog_retention_days', default=30)


def is_syslog_cleanup_enabled(db: Session) -> bool:
    """Check if syslog cleanup is enabled"""
    return get_setting_as_bool(db, 'syslog_cleanup_enabled', default=True)


def get_syslog_cleanup_hour(db: Session) -> int:
    """Get hour when syslog cleanup should run"""
    return get_setting_as_int(db, 'syslog_cleanup_hour', default=2)


def set_pending_changes(db: Session, value: bool) -> None:
    """Set pending changes flag"""
    setting = db.query(Settings).filter(Settings.key == 'pending_changes').first()
    if setting:
        setting.value = 'true' if value else 'false'
        setting.updated_at = datetime.utcnow()
        db.commit()


def has_pending_changes(db: Session) -> bool:
    """Check if there are pending changes"""
    return get_setting_as_bool(db, 'pending_changes', default=False)
