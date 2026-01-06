#!/bin/bash

echo "Starting DHCP Server..."

# Find backend container IP address (DHCP server is in host network mode)
echo "Looking for backend container IP..."
BACKEND_HOST=${BACKEND_SYSLOG_HOST:-backend}
BACKEND_PORT=${BACKEND_SYSLOG_PORT:-514}

# Try to resolve backend hostname
BACKEND_IP=$(getent hosts ${BACKEND_HOST} 2>/dev/null | awk '{ print $1 }' | head -1)

if [ -z "$BACKEND_IP" ]; then
    # Fallback: try to find backend on Docker gateway + 2 (common pattern)
    GATEWAY=$(ip route | grep default | awk '{print $3}')
    if [ -n "$GATEWAY" ]; then
        # Backend is usually on gateway IP + 1 or 2
        BACKEND_IP=$(echo $GATEWAY | awk -F. '{print $1"."$2"."$3"."$4+1}')
        echo "ℹ️  Trying backend at Docker gateway+1: $BACKEND_IP"
    fi
fi

if [ -z "$BACKEND_IP" ]; then
    echo "⚠️  WARNING: Could not find backend IP, syslog forwarding disabled"
    echo "⚠️  Logs will only be written to /var/log/dhcp/"
else
    echo "✓ Found backend at: $BACKEND_IP:$BACKEND_PORT"
    # Configure rsyslog to forward to backend
    cat > /etc/rsyslog.d/90-backend-forward.conf << EOF
# Forward DHCP logs to backend syslog server
local7.* @@${BACKEND_IP}:${BACKEND_PORT}
EOF
    echo "Starting rsyslog for log forwarding to ${BACKEND_IP}:${BACKEND_PORT}..."
fi

# Start rsyslog
rsyslogd

# Wait a bit for rsyslog to start
sleep 2

# Check if dhcpd.conf exists
if [ ! -f /dhcp-config/dhcpd.conf ]; then
    echo "WARNING: /dhcp-config/dhcpd.conf not found!"
    echo "Creating minimal default configuration..."
    cat > /dhcp-config/dhcpd.conf << 'EOF'
# Default DHCP configuration
# Please generate configuration from DHCP Admin interface

default-lease-time 600;
max-lease-time 7200;
authoritative;

# Example subnet (disabled)
# subnet 192.168.1.0 netmask 255.255.255.0 {
#   option routers 192.168.1.1;
#   option domain-name-servers 8.8.8.8;
# }
EOF
fi

echo "Using configuration: /dhcp-config/dhcpd.conf"
echo "Configuration preview:"
head -20 /dhcp-config/dhcpd.conf

# Start DHCP server in foreground
# -f = run in foreground
# -d = log to stderr (which will be captured by rsyslog)
# -cf = config file
echo "Starting ISC DHCP Server..."
exec dhcpd -f -d -cf /dhcp-config/dhcpd.conf
