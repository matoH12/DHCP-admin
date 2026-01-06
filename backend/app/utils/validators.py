"""
Validation utilities for hostnames, MAC addresses, and IP addresses
"""
import re
from ipaddress import IPv4Address, IPv4Network, AddressValueError
from typing import Optional


def validate_hostname(hostname: str) -> tuple[bool, Optional[str]]:
    """
    Validate hostname according to requirements:
    - Only alphanumeric characters, hyphens, and underscores
    - No diacritics, spaces, or special characters
    - Maximum 63 characters (DNS label limit)

    Args:
        hostname: The hostname to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not hostname:
        return False, "Hostname cannot be empty"

    if len(hostname) > 63:
        return False, "Hostname cannot exceed 63 characters (DNS label limit)"

    # Check for valid characters: alphanumeric, hyphens, underscores only
    pattern = r'^[a-zA-Z0-9_-]+$'
    if not re.match(pattern, hostname):
        return False, "Hostname can only contain alphanumeric characters, hyphens, and underscores"

    # Hostname cannot start or end with hyphen
    if hostname.startswith('-') or hostname.endswith('-'):
        return False, "Hostname cannot start or end with a hyphen"

    return True, None


def normalize_mac_address(mac: str) -> str:
    """
    Normalize MAC address to standard format XX:XX:XX:XX:XX:XX

    Args:
        mac: MAC address in various formats

    Returns:
        Normalized MAC address in XX:XX:XX:XX:XX:XX format
    """
    # Remove all separators and convert to uppercase
    mac_clean = mac.replace(':', '').replace('-', '').replace('.', '').upper()

    # Add colons every 2 characters
    return ':'.join(mac_clean[i:i+2] for i in range(0, 12, 2))


def validate_mac_address(mac: str) -> tuple[bool, Optional[str]]:
    """
    Validate MAC address format.
    Accepts formats: XX:XX:XX:XX:XX:XX, XX-XX-XX-XX-XX-XX, XXXXXXXXXXXX

    Args:
        mac: The MAC address to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not mac:
        return False, "MAC address cannot be empty"

    try:
        # Try to normalize the MAC address
        normalized = normalize_mac_address(mac)

        # Validate format: XX:XX:XX:XX:XX:XX with hex digits
        pattern = r'^([0-9A-F]{2}:){5}[0-9A-F]{2}$'
        if not re.match(pattern, normalized):
            return False, "Invalid MAC address format. Expected format: XX:XX:XX:XX:XX:XX"

        return True, None
    except Exception:
        return False, "Invalid MAC address format"


def validate_ip_address(ip: str) -> tuple[bool, Optional[str]]:
    """
    Validate IPv4 address format

    Args:
        ip: The IP address to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not ip:
        return False, "IP address cannot be empty"

    try:
        IPv4Address(ip)
        return True, None
    except AddressValueError:
        return False, "Invalid IPv4 address format"


def validate_ip_in_range(ip: str, network_address: str, cidr: int) -> tuple[bool, Optional[str]]:
    """
    Validate that an IP address is within a specific network range

    Args:
        ip: The IP address to validate
        network_address: The network address (e.g., "192.168.1.0")
        cidr: The CIDR notation (e.g., 24 for /24)

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        ip_obj = IPv4Address(ip)
        network_obj = IPv4Network(f"{network_address}/{cidr}", strict=False)

        if ip_obj not in network_obj:
            return False, f"IP address {ip} is not in network {network_address}/{cidr}"

        # Check if it's network or broadcast address
        if ip_obj == network_obj.network_address:
            return False, f"Cannot use network address {ip}"

        if ip_obj == network_obj.broadcast_address:
            return False, f"Cannot use broadcast address {ip}"

        return True, None
    except (AddressValueError, ValueError) as e:
        return False, str(e)


def validate_cidr(cidr: int) -> tuple[bool, Optional[str]]:
    """
    Validate CIDR notation

    Args:
        cidr: The CIDR value (0-32)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(cidr, int):
        return False, "CIDR must be an integer"

    if cidr < 0 or cidr > 32:
        return False, "CIDR must be between 0 and 32"

    # Warn about unusual CIDR values
    if cidr < 8:
        return True, "Warning: Very large network (CIDR < 8)"

    if cidr > 30:
        return False, "CIDR must be 30 or less for usable networks"

    return True, None


def validate_network_address(network: str, cidr: int) -> tuple[bool, Optional[str]]:
    """
    Validate that a network address is valid and properly formatted

    Args:
        network: The network address
        cidr: The CIDR notation

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        network_obj = IPv4Network(f"{network}/{cidr}", strict=False)

        # Check if the provided network address is the actual network address
        if str(network_obj.network_address) != network:
            return False, f"Network address should be {network_obj.network_address} for /{cidr}"

        return True, None
    except (AddressValueError, ValueError) as e:
        return False, str(e)
