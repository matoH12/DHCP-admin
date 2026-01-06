"""
DHCP Configuration API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from typing import List
from ...database import get_db
from ...dependencies import get_current_user
from ...schemas.dhcp_config import DHCPConfig, DHCPConfigSummary, DHCPGenerateResponse
from ...services import dhcp_generator
from ...models.user import User

router = APIRouter(prefix="/dhcp", tags=["DHCP Configuration"])


@router.post("/generate", response_model=DHCPGenerateResponse)
def generate_dhcp_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate DHCP configuration file and save to database

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Generation response with version and file path

    Raises:
        HTTPException: If generation fails
    """
    try:
        content, file_path = dhcp_generator.generate_and_save_config(
            db,
            user_id=current_user.id,
            save_to_db=True
        )

        # Get the newly created config
        active_config = dhcp_generator.get_active_config(db)

        return DHCPGenerateResponse(
            message="DHCP configuration generated successfully",
            version=active_config.version,
            file_path=file_path,
            generated_at=active_config.generated_at
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate DHCP configuration: {str(e)}"
        )


@router.get("/preview")
def preview_dhcp_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Preview DHCP configuration without saving

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Configuration file content as JSON
    """
    try:
        content = dhcp_generator.generate_dhcpd_conf(db)
        return {"config_content": content}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate preview: {str(e)}"
        )


@router.get("/active", response_model=DHCPConfig)
def get_active_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the currently active DHCP configuration

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Active DHCP configuration

    Raises:
        HTTPException: If no active config found
    """
    config = dhcp_generator.get_active_config(db)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active DHCP configuration found"
        )
    return config


@router.get("/download", response_class=PlainTextResponse)
def download_active_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download the currently active DHCP configuration as plain text file

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Configuration file content as downloadable plain text

    Raises:
        HTTPException: If no active config found
    """
    config = dhcp_generator.get_active_config(db)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active DHCP configuration found"
        )

    return PlainTextResponse(
        content=config.config_content,
        headers={
            "Content-Disposition": f"attachment; filename=dhcpd-v{config.version}.conf"
        }
    )


@router.get("/history", response_model=List[DHCPConfigSummary])
def get_config_history(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get DHCP configuration generation history

    Args:
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of DHCP configuration summaries
    """
    configs = dhcp_generator.get_config_history(db, limit=limit)

    # Convert to summary format
    summaries = []
    for config in configs:
        summaries.append({
            "id": config.id,
            "version": config.version,
            "file_path": config.file_path,
            "generated_at": config.generated_at,
            "generated_by": config.generated_by,
            "is_active": config.is_active,
            "content_length": len(config.config_content)
        })

    return summaries


@router.get("/{config_id}", response_model=DHCPConfig)
def get_config_by_id(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific DHCP configuration by ID

    Args:
        config_id: Configuration ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        DHCP configuration

    Raises:
        HTTPException: If config not found
    """
    from ...models.dhcp_config import DHCPConfig as DHCPConfigModel

    config = db.query(DHCPConfigModel).filter(DHCPConfigModel.id == config_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DHCP configuration with ID {config_id} not found"
        )
    return config
