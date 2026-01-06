"""
Settings API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...database import get_db
from ...dependencies import get_current_user
from ...schemas.settings import Setting, SettingUpdate
from ...models.settings import Settings as SettingsModel
from ...models.user import User

router = APIRouter(prefix="/settings", tags=["Settings"])


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to require ADMIN role"""
    if current_user.role != 'ADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access settings"
        )
    return current_user


@router.get("/", response_model=List[Setting])
def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get all application settings (ADMIN only)

    Returns:
        List of all settings
    """
    settings = db.query(SettingsModel).all()
    return settings


@router.get("/{key}", response_model=Setting)
def get_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get a specific setting by key (ADMIN only)

    Args:
        key: Setting key
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        Setting details

    Raises:
        HTTPException: If setting not found
    """
    setting = db.query(SettingsModel).filter(SettingsModel.key == key).first()
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting with key '{key}' not found"
        )
    return setting


@router.put("/{key}", response_model=Setting)
def update_setting(
    key: str,
    setting_data: SettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update a setting value (ADMIN only)

    Args:
        key: Setting key
        setting_data: New value
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        Updated setting

    Raises:
        HTTPException: If setting not found
    """
    setting = db.query(SettingsModel).filter(SettingsModel.key == key).first()
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting with key '{key}' not found"
        )

    # Validate specific settings
    if key == 'syslog_retention_days':
        try:
            days = int(setting_data.value)
            if days < 1 or days > 3650:  # Between 1 day and 10 years
                raise ValueError("Days must be between 1 and 3650")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid value for syslog_retention_days: {str(e)}"
            )

    if key == 'syslog_cleanup_enabled':
        if setting_data.value.lower() not in ['true', 'false']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="syslog_cleanup_enabled must be 'true' or 'false'"
            )

    if key == 'syslog_cleanup_hour':
        try:
            hour = int(setting_data.value)
            if hour < 0 or hour > 23:
                raise ValueError("Hour must be between 0 and 23")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid value for syslog_cleanup_hour: {str(e)}"
            )

    setting.value = setting_data.value
    db.commit()
    db.refresh(setting)

    return setting
