"""Docker container management utilities"""
import subprocess
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

def restart_dhcp_container() -> Tuple[bool, str]:
    """
    Restart DHCP server Docker container

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        result = subprocess.run(
            ['docker', 'compose', 'restart', 'dhcp-server'],
            cwd='/home/matoh12/dhcp-admin',
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            logger.info("DHCP server container restarted successfully")
            return True, "DHCP server restarted successfully"
        else:
            error_msg = result.stderr or result.stdout
            logger.error(f"Failed to restart DHCP container: {error_msg}")
            return False, f"Failed to restart: {error_msg}"

    except subprocess.TimeoutExpired:
        return False, "Restart operation timed out"
    except Exception as e:
        logger.error(f"Error restarting DHCP container: {str(e)}")
        return False, f"Unexpected error: {str(e)}"
