"""Docker container management utilities"""
import subprocess
import logging
import os
from typing import Tuple

logger = logging.getLogger(__name__)

def restart_dhcp_container() -> Tuple[bool, str]:
    """
    Restart DHCP server Docker container

    Uses container name instead of docker-compose to avoid hardcoded paths.
    Container name is configurable via DHCP_CONTAINER_NAME env var.

    Returns:
        Tuple of (success: bool, message: str)
    """
    # Get container name from environment or use default
    container_name = os.getenv('DHCP_CONTAINER_NAME', 'dhcp-admin-dhcp-server')

    try:
        result = subprocess.run(
            ['docker', 'restart', container_name],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            logger.info(f"DHCP server container '{container_name}' restarted successfully")
            return True, "DHCP server restarted successfully"
        else:
            error_msg = result.stderr or result.stdout
            logger.error(f"Failed to restart DHCP container '{container_name}': {error_msg}")
            return False, f"Failed to restart: {error_msg}"

    except subprocess.TimeoutExpired:
        logger.error(f"Restart of container '{container_name}' timed out")
        return False, "Restart operation timed out"
    except Exception as e:
        logger.error(f"Error restarting DHCP container '{container_name}': {str(e)}")
        return False, f"Unexpected error: {str(e)}"
