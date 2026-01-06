"""
DHCP Logs API endpoints - File-based log viewing and management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
import os
import glob
from ...dependencies import get_current_user
from ...models.user import User

router = APIRouter(prefix="/logs", tags=["Logs"])

DHCP_LOG_DIR = "/var/log/dhcp"


def read_log_file(file_path: str, lines: int = 100, search: Optional[str] = None) -> List[dict]:
    """
    Read last N lines from log file

    Args:
        file_path: Path to log file
        lines: Number of lines to read from end
        search: Optional search filter

    Returns:
        List of log line dictionaries
    """
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, 'r') as f:
            all_lines = f.readlines()

        # Get last N lines
        last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

        # Filter by search term if provided
        if search:
            last_lines = [line for line in last_lines if search.lower() in line.lower()]

        # Parse lines into structured format
        result = []
        for idx, line in enumerate(last_lines):
            line = line.strip()
            if not line:
                continue

            result.append({
                "line_number": len(all_lines) - len(last_lines) + idx + 1,
                "content": line,
                "timestamp": extract_timestamp(line)
            })

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading log file: {str(e)}"
        )


def extract_timestamp(log_line: str) -> Optional[str]:
    """Extract timestamp from log line if present"""
    # Basic timestamp extraction - can be enhanced
    parts = log_line.split()
    if len(parts) >= 3:
        # Try to parse common syslog format: "Jan 6 12:34:56"
        try:
            return " ".join(parts[:3])
        except:
            pass
    return None


@router.get("/dhcp", response_model=dict)
def get_dhcp_logs(
    lines: int = Query(100, le=1000, description="Number of recent lines to retrieve"),
    search: Optional[str] = Query(None, description="Search term to filter logs"),
    current_user: User = Depends(get_current_user)
):
    """
    Get DHCP server logs

    Args:
        lines: Number of recent lines to retrieve (max 1000)
        search: Optional search filter
        current_user: Current authenticated user

    Returns:
        Dictionary with log data and metadata
    """
    dhcpd_log = os.path.join(DHCP_LOG_DIR, "dhcpd.log")

    log_lines = read_log_file(dhcpd_log, lines=lines, search=search)

    # Get file size and modification time
    file_info = {}
    if os.path.exists(dhcpd_log):
        stat = os.stat(dhcpd_log)
        file_info = {
            "size_bytes": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }

    return {
        "logs": log_lines,
        "total_lines": len(log_lines),
        "file_info": file_info,
        "log_file": "dhcpd.log"
    }


@router.get("/files", response_model=List[dict])
def list_log_files(
    current_user: User = Depends(get_current_user)
):
    """
    List all available log files

    Args:
        current_user: Current authenticated user

    Returns:
        List of log files with metadata
    """
    if not os.path.exists(DHCP_LOG_DIR):
        return []

    log_files = []
    for file_path in glob.glob(os.path.join(DHCP_LOG_DIR, "*.log")):
        stat = os.stat(file_path)
        log_files.append({
            "name": os.path.basename(file_path),
            "path": file_path,
            "size_bytes": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        })

    # Sort by modification time, newest first
    log_files.sort(key=lambda x: x["modified"], reverse=True)

    return log_files


@router.delete("/clear", status_code=status.HTTP_200_OK)
def clear_dhcp_logs(
    current_user: User = Depends(get_current_user)
):
    """
    Clear (truncate) all DHCP log files

    Args:
        current_user: Current authenticated user

    Returns:
        Dictionary with number of files cleared

    Raises:
        HTTPException: If user not admin
    """
    if current_user.role != 'ADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can clear logs"
        )

    if not os.path.exists(DHCP_LOG_DIR):
        return {"cleared_files": 0, "message": "Log directory does not exist"}

    cleared = 0
    errors = []

    for file_path in glob.glob(os.path.join(DHCP_LOG_DIR, "*.log")):
        try:
            # Truncate file (clear contents but keep file)
            with open(file_path, 'w') as f:
                pass
            cleared += 1
        except Exception as e:
            errors.append(f"{os.path.basename(file_path)}: {str(e)}")

    result = {
        "cleared_files": cleared,
        "message": f"Cleared {cleared} log file(s)"
    }

    if errors:
        result["errors"] = errors

    return result


@router.delete("/file/{filename}", status_code=status.HTTP_200_OK)
def delete_log_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific log file

    Args:
        filename: Name of log file to delete
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        HTTPException: If user not admin or file not found
    """
    if current_user.role != 'ADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete logs"
        )

    # Security: prevent path traversal
    if ".." in filename or "/" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename"
        )

    file_path = os.path.join(DHCP_LOG_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log file '{filename}' not found"
        )

    try:
        os.remove(file_path)
        return {"message": f"Log file '{filename}' deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting file: {str(e)}"
        )
