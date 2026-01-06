#!/bin/bash

echo "Starting DHCP Server..."

# Configure syslog forwarding to backend
# DHCP server is in host network mode, backend exposes syslog on 0.0.0.0:514
# Find Docker bridge IP (docker0) where backend is accessible
BACKEND_PORT=${BACKEND_SYSLOG_PORT:-514}

# Find docker0 bridge IP (Docker's default bridge gateway)
DOCKER_BRIDGE_IP=$(ip -4 addr show docker0 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}')

if [ -z "$DOCKER_BRIDGE_IP" ]; then
    # Fallback: try other common Docker bridge patterns
    for iface in br-* docker_gwbridge; do
        DOCKER_BRIDGE_IP=$(ip -4 addr show $iface 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -1)
        if [ -n "$DOCKER_BRIDGE_IP" ]; then
            echo "✓ Found Docker bridge on $iface: $DOCKER_BRIDGE_IP"
            break
        fi
    done
fi

if [ -z "$DOCKER_BRIDGE_IP" ]; then
    echo "⚠️  WARNING: Could not find Docker bridge IP"
    echo "⚠️  Syslog forwarding disabled - logs only in /var/log/dhcp/"
else
    echo "✓ Configuring syslog forwarding to Docker bridge: ${DOCKER_BRIDGE_IP}:${BACKEND_PORT}"

    # Configure rsyslog to forward to backend via Docker bridge
    cat > /etc/rsyslog.d/90-backend-forward.conf << EOF
# Forward DHCP logs to backend syslog server via Docker bridge
# DHCP server uses host network, backend accessible on Docker bridge IP
local7.* @@${DOCKER_BRIDGE_IP}:${BACKEND_PORT}
EOF

    echo "✓ Rsyslog configured to forward to ${DOCKER_BRIDGE_IP}:${BACKEND_PORT}"
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
