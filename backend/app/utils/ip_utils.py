"""
IP address utility functions
"""
from ipaddress import IPv4Network, IPv4Address
from typing import List, Set


def calculate_network_info(network_address: str, cidr: int) -> dict:
    """
    Calculate network information from network address and CIDR

    Args:
        network_address: Network address (e.g., "192.168.1.0")
        cidr: CIDR notation (e.g., 24)

    Returns:
        Dictionary with network information
    """
    network = IPv4Network(f"{network_address}/{cidr}", strict=False)

    return {
        "network_address": str(network.network_address),
        "broadcast_address": str(network.broadcast_address),
        "netmask": str(network.netmask),
        "cidr": cidr,
        "total_addresses": network.num_addresses,
        "usable_addresses": network.num_addresses - 2,  # Exclude network and broadcast
        "first_usable": str(network.network_address + 1),
        "last_usable": str(network.broadcast_address - 1),
    }


def get_all_ips_in_range(network_address: str, cidr: int, exclude_gateway: str = None) -> List[str]:
    """
    Get all usable IP addresses in a network range

    Args:
        network_address: Network address (e.g., "192.168.1.0")
        cidr: CIDR notation (e.g., 24)
        exclude_gateway: Optional gateway IP to exclude

    Returns:
        List of all usable IP addresses
    """
    network = IPv4Network(f"{network_address}/{cidr}", strict=False)
    ips = []

    for ip in network.hosts():  # hosts() automatically excludes network and broadcast
        ip_str = str(ip)
        if exclude_gateway and ip_str == exclude_gateway:
            continue
        ips.append(ip_str)

    return ips


def get_available_ips(
    network_address: str,
    cidr: int,
    assigned_ips: Set[str],
    gateway: str = None
) -> List[str]:
    """
    Get list of available (unassigned) IP addresses in a range

    Args:
        network_address: Network address (e.g., "192.168.1.0")
        cidr: CIDR notation (e.g., 24)
        assigned_ips: Set of already assigned IP addresses
        gateway: Optional gateway IP to exclude

    Returns:
        List of available IP addresses, sorted
    """
    all_ips = get_all_ips_in_range(network_address, cidr, exclude_gateway=gateway)
    available = [ip for ip in all_ips if ip not in assigned_ips]
    return sorted(available, key=lambda ip: IPv4Address(ip))


def suggest_next_ip(
    network_address: str,
    cidr: int,
    assigned_ips: Set[str],
    gateway: str = None
) -> str:
    """
    Suggest the next available IP address in sequential order

    Args:
        network_address: Network address (e.g., "192.168.1.0")
        cidr: CIDR notation (e.g., 24)
        assigned_ips: Set of already assigned IP addresses
        gateway: Optional gateway IP to exclude

    Returns:
        Next available IP address, or None if range is full
    """
    available = get_available_ips(network_address, cidr, assigned_ips, gateway)
    return available[0] if available else None


def calculate_range_statistics(
    network_address: str,
    cidr: int,
    assigned_count: int,
    gateway: str = None
) -> dict:
    """
    Calculate statistics for an IP range

    Args:
        network_address: Network address (e.g., "192.168.1.0")
        cidr: CIDR notation (e.g., 24)
        assigned_count: Number of assigned IPs
        gateway: Optional gateway IP (counts as 1 used IP)

    Returns:
        Dictionary with range statistics
    """
    network_info = calculate_network_info(network_address, cidr)
    total_usable = network_info["usable_addresses"]

    # If there's a gateway, it counts as one used IP
    used_by_infrastructure = 1 if gateway else 0
    used_total = assigned_count + used_by_infrastructure
    available = total_usable - used_total

    return {
        **network_info,
        "total_usable": total_usable,
        "assigned": assigned_count,
        "infrastructure": used_by_infrastructure,  # Gateway, etc.
        "used_total": used_total,
        "available": available,
        "utilization_percent": round((used_total / total_usable * 100), 2) if total_usable > 0 else 0,
    }
