#!/bin/bash
#
# DHCP Admin - Deployment Configuration Wizard
# Interactive configuration for different deployment scenarios
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CONFIG_FILE=".deployment-config"

echo -e "${GREEN}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   DHCP Admin - Deployment Configuration Wizard   ║${NC}"
echo -e "${GREEN}╔═══════════════════════════════════════════════════╗${NC}\n"

# Function to ask yes/no questions
ask_yes_no() {
    local question=$1
    local default=${2:-n}

    if [ "$default" = "y" ]; then
        prompt="[Y/n]"
    else
        prompt="[y/N]"
    fi

    echo -e "${YELLOW}${question} ${prompt}:${NC}"
    read -r answer
    answer=${answer:-$default}

    if [[ "$answer" =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

# 1. SSL/TLS Configuration
echo -e "${BLUE}═══ 1. SSL/TLS Configuration ═══${NC}\n"
echo "Vyber typ SSL certifikátu:"
echo "  1) Self-signed certificate (jednoduchý, intranet)"
echo "  2) Let's Encrypt (automatický, verejná doména)"
echo "  3) Vlastný certifikát (nahrať vlastný)"
echo "  4) Žiadny SSL - len HTTP (za proxy/load balancer)"
echo ""
read -p "Výber [1-4]: " SSL_CHOICE
SSL_CHOICE=${SSL_CHOICE:-1}

# 2. CORS Configuration
echo -e "\n${BLUE}═══ 2. CORS Configuration ═══${NC}\n"
if ask_yes_no "Povoliť CORS?" "y"; then
    CORS_ENABLED="true"
    echo -e "${YELLOW}Zadaj CORS origins (oddelené čiarkou):${NC}"
    echo "Príklad: https://admin.example.com,https://example.com"
    read -r CORS_ORIGINS
    CORS_ORIGINS=${CORS_ORIGINS:-"http://localhost:3002"}
else
    CORS_ENABLED="false"
    CORS_ORIGINS=""
fi

# 3. Security Features
echo -e "\n${BLUE}═══ 3. Security Features ═══${NC}\n"

if ask_yes_no "Zapnúť rate limiting?" "y"; then
    RATE_LIMITING="true"
else
    RATE_LIMITING="false"
fi

if ask_yes_no "Zapnúť security headers?" "y"; then
    SECURITY_HEADERS="true"
else
    SECURITY_HEADERS="false"
fi

if ask_yes_no "Zapnúť API dokumentáciu (/api/docs)?" "n"; then
    API_DOCS="true"
else
    API_DOCS="false"
fi

# 4. Network Mode
echo -e "\n${BLUE}═══ 4. Network Configuration ═══${NC}\n"
echo "DHCP server network mode:"
echo "  1) Bridge mode (development/test)"
echo "  2) Host mode (production - potrebné pre DHCP)"
echo ""
read -p "Výber [1-2]: " NETWORK_CHOICE
NETWORK_CHOICE=${NETWORK_CHOICE:-1}

if [ "$NETWORK_CHOICE" = "2" ]; then
    DHCP_NETWORK_MODE="host"
else
    DHCP_NETWORK_MODE="bridge"
fi

# 5. Domain/Hostname
echo -e "\n${BLUE}═══ 5. Domain/Hostname ═══${NC}\n"
echo -e "${YELLOW}Zadaj domain/hostname (default: localhost):${NC}"
read -r DOMAIN
DOMAIN=${DOMAIN:-localhost}

# Save configuration
echo -e "\n${GREEN}Ukladám konfiguráciu...${NC}"
cat > $CONFIG_FILE << EOF
# DHCP Admin Deployment Configuration
# Generated: $(date)

SSL_CHOICE=$SSL_CHOICE
SSL_TYPE=$([ "$SSL_CHOICE" = "1" ] && echo "self-signed" || [ "$SSL_CHOICE" = "2" ] && echo "letsencrypt" || [ "$SSL_CHOICE" = "3" ] && echo "custom" || echo "none")
CORS_ENABLED=$CORS_ENABLED
CORS_ORIGINS=$CORS_ORIGINS
RATE_LIMITING=$RATE_LIMITING
SECURITY_HEADERS=$SECURITY_HEADERS
API_DOCS=$API_DOCS
DHCP_NETWORK_MODE=$DHCP_NETWORK_MODE
DOMAIN=$DOMAIN
EOF

echo -e "${GREEN}✓ Konfigurácia uložená do $CONFIG_FILE${NC}\n"

# Summary
echo -e "${GREEN}═══ Prehľad konfigurácie ═══${NC}"
echo -e "SSL/TLS: ${YELLOW}$([ "$SSL_CHOICE" = "1" ] && echo "Self-signed" || [ "$SSL_CHOICE" = "2" ] && echo "Let's Encrypt" || [ "$SSL_CHOICE" = "3" ] && echo "Vlastný" || echo "HTTP only")${NC}"
echo -e "CORS: ${YELLOW}$([ "$CORS_ENABLED" = "true" ] && echo "Zapnuté ($CORS_ORIGINS)" || echo "Vypnuté")${NC}"
echo -e "Rate Limiting: ${YELLOW}$([ "$RATE_LIMITING" = "true" ] && echo "Zapnuté" || echo "Vypnuté")${NC}"
echo -e "Security Headers: ${YELLOW}$([ "$SECURITY_HEADERS" = "true" ] && echo "Zapnuté" || echo "Vypnuté")${NC}"
echo -e "API Docs: ${YELLOW}$([ "$API_DOCS" = "true" ] && echo "Zapnuté" || echo "Vypnuté")${NC}"
echo -e "DHCP Network: ${YELLOW}$DHCP_NETWORK_MODE${NC}"
echo -e "Domain: ${YELLOW}$DOMAIN${NC}\n"

# Generate files based on configuration
echo -e "${GREEN}Generujem konfiguračné súbory...${NC}\n"

# Generate .env file
cat > .env.custom << EOF
# Custom deployment configuration
# Generated: $(date)

APP_NAME=DHCP Admin
DEBUG=$([ "$API_DOCS" = "true" ] && echo "true" || echo "false")

# Security
ENABLE_RATE_LIMITING=$RATE_LIMITING
ENABLE_SECURITY_HEADERS=$SECURITY_HEADERS
ENABLE_CORS=$CORS_ENABLED
CORS_ORIGINS=$CORS_ORIGINS

# SSL/TLS
SSL_ENABLED=$([ "$SSL_CHOICE" != "4" ] && echo "true" || echo "false")
DOMAIN=$DOMAIN

# Database
DATABASE_URL=sqlite:///./data/dhcp-admin.db

# DHCP
DHCP_CONFIG_PATH=/dhcp-config/dhcpd.conf
DHCP_NETWORK_MODE=$DHCP_NETWORK_MODE
EOF

echo -e "${GREEN}✓ Created: .env.custom${NC}"

# Next steps based on SSL choice
echo -e "\n${YELLOW}═══ Ďalšie kroky ═══${NC}\n"

case $SSL_CHOICE in
    1)
        echo "1. Vygeneruj self-signed certifikát:"
        echo -e "   ${YELLOW}./scripts/init-secrets.sh${NC}"
        ;;
    2)
        echo "1. Vygeneruj secrets:"
        echo -e "   ${YELLOW}./scripts/init-secrets.sh${NC}"
        echo "2. Nainštaluj certbot a vygeneruj Let's Encrypt certifikát:"
        echo -e "   ${YELLOW}./scripts/setup-letsencrypt.sh $DOMAIN${NC}"
        ;;
    3)
        echo "1. Vygeneruj secrets:"
        echo -e "   ${YELLOW}./scripts/init-secrets.sh${NC}"
        echo "2. Nahraj vlastný certifikát:"
        echo -e "   ${YELLOW}cp your-cert.pem nginx/ssl/cert.pem${NC}"
        echo -e "   ${YELLOW}cp your-key.pem nginx/ssl/key.pem${NC}"
        ;;
    4)
        echo "1. Vygeneruj secrets (bez SSL):"
        echo -e "   ${YELLOW}./scripts/init-secrets.sh --no-ssl${NC}"
        echo -e "${RED}⚠ Upozornenie: HTTP-only režim! Používaj len za HTTPS proxy/load balancer!${NC}"
        ;;
esac

echo ""
echo "3. Spusti aplikáciu:"
echo -e "   ${YELLOW}./scripts/start-deployment.sh${NC}"

echo -e "\n${GREEN}═══ Konfigurácia dokončená! ═══${NC}\n"
