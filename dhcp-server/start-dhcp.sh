#!/bin/bash

echo "Starting DHCP Server..."

# Start rsyslog to forward logs to backend
echo "Starting rsyslog for log forwarding..."
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
