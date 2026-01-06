#!/bin/bash
#
# Renew self-signed SSL certificate
# Run this script annually to renew the certificate
#

set -e

NGINX_SSL_DIR="./nginx/ssl"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== SSL Certificate Renewal ===${NC}\n"

# Check if certificate exists
if [ ! -f "$NGINX_SSL_DIR/cert.pem" ]; then
    echo -e "${YELLOW}No existing certificate found. Run ./scripts/init-secrets.sh first.${NC}"
    exit 1
fi

# Get certificate info
echo -e "${YELLOW}Current certificate:${NC}"
openssl x509 -in "$NGINX_SSL_DIR/cert.pem" -noout -subject -dates

# Backup old certificate
echo -e "\n${YELLOW}Backing up old certificate...${NC}"
cp "$NGINX_SSL_DIR/cert.pem" "$NGINX_SSL_DIR/cert.pem.bak"
cp "$NGINX_SSL_DIR/key.pem" "$NGINX_SSL_DIR/key.pem.bak"

# Get domain from old certificate
OLD_DOMAIN=$(openssl x509 -in "$NGINX_SSL_DIR/cert.pem" -noout -subject | sed -n 's/.*CN=\([^,]*\).*/\1/p')

echo -e "${YELLOW}Enter domain/hostname (current: $OLD_DOMAIN, press Enter to keep):${NC}"
read -r DOMAIN
DOMAIN=${DOMAIN:-$OLD_DOMAIN}

# Generate new certificate
echo -e "\n${GREEN}Generating new certificate for: $DOMAIN${NC}"
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$NGINX_SSL_DIR/key.pem" \
    -out "$NGINX_SSL_DIR/cert.pem" \
    -subj "/C=SK/ST=Slovakia/L=Bratislava/O=DHCP Admin/CN=$DOMAIN"

chmod 600 "$NGINX_SSL_DIR/key.pem"
chmod 644 "$NGINX_SSL_DIR/cert.pem"

echo -e "${GREEN}✓ New certificate generated${NC}"
echo -e "${YELLOW}Valid for 365 days from today${NC}\n"

# Show new certificate info
echo -e "${GREEN}New certificate details:${NC}"
openssl x509 -in "$NGINX_SSL_DIR/cert.pem" -noout -subject -dates

echo -e "\n${YELLOW}Restart nginx to apply new certificate:${NC}"
echo -e "${YELLOW}docker compose -f docker-compose.prod.yml restart nginx${NC}\n"
