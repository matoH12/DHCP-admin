FROM ubuntu:22.04

# Install ISC DHCP server and rsyslog
RUN apt-get update && \
    apt-get install -y \
    isc-dhcp-server \
    rsyslog \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /var/lib/dhcp /dhcp-config

# Copy startup script
COPY start-dhcp.sh /start-dhcp.sh
RUN chmod +x /start-dhcp.sh

# Copy rsyslog configuration for forwarding to backend
COPY rsyslog.conf /etc/rsyslog.d/50-dhcp-forward.conf

# Default lease file
RUN touch /var/lib/dhcp/dhcpd.leases

# Expose DHCP ports
EXPOSE 67/udp 68/udp

# Start script
CMD ["/start-dhcp.sh"]
