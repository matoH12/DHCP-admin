#!/bin/bash
#
# Setup Let's Encrypt SSL certificate
#

set -e

DOMAIN=$1
EMAIL=${2:-admin@$DOMAIN}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$DOMAIN" ]; then
    echo -e "${RED}Error: Domain is required${NC}"
    echo "Usage: $0 <domain> [email]"
    echo "Example: $0 dhcp.example.com admin@example.com"
    exit 1
fi

echo -e "${GREEN}=== Let's Encrypt Setup ===${NC}\n"
echo -e "Domain: ${YELLOW}$DOMAIN${NC}"
echo -e "Email: ${YELLOW}$EMAIL${NC}\n"

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo -e "${YELLOW}Certbot not found. Installing...${NC}"

    if [ -f /etc/debian_version ]; then
        apt update
        apt install -y certbot
    elif [ -f /etc/redhat-release ]; then
        yum install -y certbot
    else
        echo -e "${RED}Unsupported OS. Please install certbot manually.${NC}"
        exit 1
    fi
fi

# Create webroot directory
mkdir -p /var/www/certbot

# Temporary nginx config for certbot
echo -e "${YELLOW}Creating temporary nginx config...${NC}"
cat > /tmp/nginx-certbot.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name DOMAIN_PLACEHOLDER;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 200 "Certbot validation server";
        }
    }
}
EOF

sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" /tmp/nginx-certbot.conf

# Start temporary nginx (if not running)
if ! docker ps | grep -q nginx-certbot; then
    echo -e "${YELLOW}Starting temporary nginx for validation...${NC}"
    docker run -d --name nginx-certbot \
        -p 80:80 \
        -v /var/www/certbot:/var/www/certbot:ro \
        -v /tmp/nginx-certbot.conf:/etc/nginx/nginx.conf:ro \
        nginx:alpine
fi

# Request certificate
echo -e "${YELLOW}Requesting Let's Encrypt certificate...${NC}"
certbot certonly --webroot \
    -w /var/www/certbot \
    -d $DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --non-interactive

# Stop temporary nginx
docker stop nginx-certbot 2>/dev/null || true
docker rm nginx-certbot 2>/dev/null || true

# Create nginx ssl directory
mkdir -p nginx/ssl

# Link certificates
echo -e "${YELLOW}Linking certificates...${NC}"
ln -sf /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/cert.pem
ln -sf /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/key.pem

echo -e "${GREEN}✓ Let's Encrypt certificate installed${NC}"
echo -e "${GREEN}✓ Certificate linked to nginx/ssl/${NC}\n"

# Setup auto-renewal
echo -e "${YELLOW}Setting up auto-renewal...${NC}"
if ! crontab -l | grep -q "certbot renew"; then
    (crontab -l 2>/dev/null; echo "0 0 * * 0 certbot renew --quiet && docker compose -f docker-compose.prod.yml restart nginx") | crontab -
    echo -e "${GREEN}✓ Auto-renewal cron job added (weekly check)${NC}"
else
    echo -e "${YELLOW}Auto-renewal already configured${NC}"
fi

# Test renewal
echo -e "\n${YELLOW}Testing renewal process...${NC}"
certbot renew --dry-run

echo -e "\n${GREEN}═══ Setup Complete ═══${NC}"
echo -e "${GREEN}Certificate valid for 90 days${NC}"
echo -e "${GREEN}Auto-renewal configured (weekly check)${NC}\n"

echo -e "${YELLOW}Next step: Start the application${NC}"
echo -e "${YELLOW}./scripts/start-deployment.sh${NC}\n"
