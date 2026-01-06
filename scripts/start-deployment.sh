#!/bin/bash
#
# Start DHCP Admin deployment based on configuration
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

CONFIG_FILE=".deployment-config"

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}Error: Configuration file not found${NC}"
    echo "Run ./scripts/configure-deployment.sh first"
    exit 1
fi

# Load configuration
source $CONFIG_FILE

echo -e "${GREEN}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Starting DHCP Admin Deployment               ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════╝${NC}\n"

echo -e "${YELLOW}Configuration:${NC}"
echo -e "  SSL: $SSL_TYPE"
echo -e "  CORS: $([ "$CORS_ENABLED" = "true" ] && echo "Enabled" || echo "Disabled")"
echo -e "  Rate Limiting: $([ "$RATE_LIMITING" = "true" ] && echo "Enabled" || echo "Disabled")"
echo -e "  Security Headers: $([ "$SECURITY_HEADERS" = "true" ] && echo "Enabled" || echo "Disabled")"
echo -e "  DHCP Network: $DHCP_NETWORK_MODE"
echo -e ""

# Check if secrets exist
if [ ! -d "secrets" ] && [ "$SSL_CHOICE" != "4" ]; then
    echo -e "${RED}Error: Secrets not found${NC}"
    echo "Run ./scripts/init-secrets.sh first"
    exit 1
fi

# Select nginx config
if [ "$SSL_CHOICE" = "4" ]; then
    NGINX_CONFIG="nginx/nginx-http-only.conf"
    echo -e "${YELLOW}Using HTTP-only nginx configuration${NC}"
else
    NGINX_CONFIG="nginx/nginx.conf"
    echo -e "${YELLOW}Using HTTPS nginx configuration${NC}"
fi

# Generate docker-compose override
echo -e "${YELLOW}Generating docker-compose override...${NC}"
cat > docker-compose.override.yml << EOF
version: '3.8'

services:
  backend:
    environment:
      - ENABLE_CORS=$CORS_ENABLED
      - CORS_ORIGINS=$CORS_ORIGINS
      - ENABLE_RATE_LIMITING=$RATE_LIMITING
      - ENABLE_SECURITY_HEADERS=$SECURITY_HEADERS
      - DEBUG=$([ "$API_DOCS" = "true" ] && echo "true" || echo "false")
    env_file:
      - .env.custom

  dhcp-server:
$(if [ "$DHCP_NETWORK_MODE" = "host" ]; then
    echo "    network_mode: host"
fi)

  nginx:
    volumes:
      - $NGINX_CONFIG:/etc/nginx/nginx.conf:ro
EOF

echo -e "${GREEN}✓ docker-compose.override.yml created${NC}"

# Check SSL certificates
if [ "$SSL_CHOICE" != "4" ]; then
    if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
        echo -e "${RED}Error: SSL certificates not found${NC}"
        echo "Run one of:"
        echo "  - ./scripts/init-secrets.sh (for self-signed)"
        echo "  - ./scripts/setup-letsencrypt.sh $DOMAIN (for Let's Encrypt)"
        exit 1
    fi
    echo -e "${GREEN}✓ SSL certificates found${NC}"
fi

# Start deployment
echo -e "\n${YELLOW}Starting containers...${NC}"
docker compose -f docker-compose.prod.yml up -d

# Wait for health check
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 5

# Check status
if docker compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo -e "\n${GREEN}✓ Deployment successful!${NC}\n"

    # Show access information
    if [ "$SSL_CHOICE" = "4" ]; then
        echo -e "${GREEN}Access:${NC}"
        echo -e "  HTTP: ${YELLOW}http://$(hostname -I | awk '{print $1}')${NC}"
    else
        echo -e "${GREEN}Access:${NC}"
        echo -e "  HTTPS: ${YELLOW}https://$(hostname -I | awk '{print $1}')${NC}"
        echo -e "  HTTP: ${YELLOW}http://$(hostname -I | awk '{print $1}')${NC} (redirects to HTTPS)"
    fi

    echo -e "\n${YELLOW}View logs:${NC}"
    echo -e "  docker compose -f docker-compose.prod.yml logs -f"

    echo -e "\n${YELLOW}Stop deployment:${NC}"
    echo -e "  docker compose -f docker-compose.prod.yml down"

else
    echo -e "\n${RED}✗ Deployment failed${NC}"
    echo -e "Check logs: docker compose -f docker-compose.prod.yml logs"
    exit 1
fi
