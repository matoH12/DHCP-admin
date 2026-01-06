#!/bin/bash
#
# Initialize Docker secrets for production deployment
# This script generates secure random passwords and creates secret files
#

set -e

SECRETS_DIR="./secrets"
NGINX_SSL_DIR="./nginx/ssl"
NO_SSL=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-ssl)
            NO_SSL=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== DHCP Admin - Security Initialization ===${NC}\n"

# Create secrets directory
if [ ! -d "$SECRETS_DIR" ]; then
    echo -e "${YELLOW}Creating secrets directory...${NC}"
    mkdir -p "$SECRETS_DIR"
    chmod 700 "$SECRETS_DIR"
else
    echo -e "${YELLOW}Secrets directory already exists${NC}"
fi

# Create nginx SSL directory
if [ ! -d "$NGINX_SSL_DIR" ]; then
    echo -e "${YELLOW}Creating nginx SSL directory...${NC}"
    mkdir -p "$NGINX_SSL_DIR"
    chmod 700 "$NGINX_SSL_DIR"
fi

# Function to generate random password
generate_password() {
    local length=${1:-32}
    openssl rand -base64 $length | tr -d "=+/" | cut -c1-$length
}

# Function to create secret file
create_secret() {
    local secret_name=$1
    local secret_value=$2
    local secret_file="$SECRETS_DIR/${secret_name}.txt"

    if [ -f "$secret_file" ]; then
        echo -e "${YELLOW}⚠ Secret '$secret_name' already exists. Skipping.${NC}"
        return
    fi

    echo -n "$secret_value" > "$secret_file"
    chmod 600 "$secret_file"
    echo -e "${GREEN}✓ Created secret: $secret_name${NC}"
}

# Generate SECRET_KEY (for JWT tokens)
echo -e "\n${GREEN}1. Generating SECRET_KEY...${NC}"
SECRET_KEY=$(generate_password 64)
create_secret "secret_key" "$SECRET_KEY"

# Admin credentials
echo -e "\n${GREEN}2. Setting up admin credentials...${NC}"
echo -e "${YELLOW}Please enter admin username (default: admin):${NC}"
read -r ADMIN_USERNAME
ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
create_secret "admin_username" "$ADMIN_USERNAME"

echo -e "${YELLOW}Please enter admin email (default: admin@localhost):${NC}"
read -r ADMIN_EMAIL
ADMIN_EMAIL=${ADMIN_EMAIL:-admin@localhost}
create_secret "admin_email" "$ADMIN_EMAIL"

echo -e "${YELLOW}Please enter admin password (leave empty to generate):${NC}"
read -s ADMIN_PASSWORD
if [ -z "$ADMIN_PASSWORD" ]; then
    ADMIN_PASSWORD=$(generate_password 24)
    echo -e "${GREEN}Generated password: ${YELLOW}$ADMIN_PASSWORD${NC}"
    echo -e "${RED}⚠ IMPORTANT: Save this password! It will not be shown again.${NC}"
fi
create_secret "admin_password" "$ADMIN_PASSWORD"

# Generate self-signed SSL certificate
if [ "$NO_SSL" = false ]; then
    echo -e "\n${GREEN}3. Generating self-signed SSL certificate...${NC}"
    if [ ! -f "$NGINX_SSL_DIR/cert.pem" ]; then
        echo -e "${YELLOW}Enter your domain/hostname (default: localhost):${NC}"
        read -r DOMAIN
        DOMAIN=${DOMAIN:-localhost}

        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$NGINX_SSL_DIR/key.pem" \
            -out "$NGINX_SSL_DIR/cert.pem" \
            -subj "/C=SK/ST=Slovakia/L=Bratislava/O=DHCP Admin/CN=$DOMAIN"
        chmod 600 "$NGINX_SSL_DIR/key.pem"
        chmod 644 "$NGINX_SSL_DIR/cert.pem"
        echo -e "${GREEN}✓ Self-signed SSL certificate created for: $DOMAIN${NC}"
        echo -e "${YELLOW}⚠ Valid for 365 days${NC}"
    else
        echo -e "${YELLOW}⚠ SSL certificate already exists${NC}"
    fi
else
    echo -e "\n${YELLOW}3. Skipping SSL certificate generation (--no-ssl)${NC}"
fi

# Create .env.production file
echo -e "\n${GREEN}4. Creating .env.production file...${NC}"
cat > .env.production << EOF
# Production environment variables
# Generated: $(date)

# Application
APP_NAME=DHCP Admin
DEBUG=false

# Database
DATABASE_URL=sqlite:///./data/dhcp-admin.db

# Security - DO NOT COMMIT THESE VALUES
# Use Docker secrets instead (see docker-compose.prod.yml)
SECRET_KEY=$(cat $SECRETS_DIR/secret_key.txt)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS - Change to your domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# DHCP Configuration
DHCP_CONFIG_PATH=/dhcp-config/dhcpd.conf

# Admin User
ADMIN_USERNAME=$(cat $SECRETS_DIR/admin_username.txt)
ADMIN_PASSWORD=$(cat $SECRETS_DIR/admin_password.txt)
ADMIN_EMAIL=$(cat $SECRETS_DIR/admin_email.txt)
EOF

chmod 600 .env.production
echo -e "${GREEN}✓ Created .env.production${NC}"

# Create .gitignore for secrets
echo -e "\n${GREEN}5. Updating .gitignore...${NC}"
cat >> .gitignore << EOF

# Security - Never commit secrets!
secrets/
.env.production
nginx/ssl/*.pem
nginx/ssl/*.key
EOF
echo -e "${GREEN}✓ Updated .gitignore${NC}"

# Summary
echo -e "\n${GREEN}=== Setup Complete ===${NC}\n"
echo -e "${GREEN}✓ Secrets directory: $SECRETS_DIR${NC}"
echo -e "${GREEN}✓ SSL certificates: $NGINX_SSL_DIR${NC}"
echo -e "${GREEN}✓ Environment file: .env.production${NC}\n"

echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Review docker-compose.prod.yml"
echo -e "2. Update CORS_ORIGINS in .env.production with your domain"
echo -e "3. Start the application:"
echo -e "   ${YELLOW}docker compose -f docker-compose.prod.yml up -d${NC}"
echo -e "4. Access via HTTPS: ${YELLOW}https://your-server-ip${NC}\n"

echo -e "${RED}⚠ SECURITY WARNINGS:${NC}"
echo -e "- Keep the secrets/ directory secure (chmod 700)"
echo -e "- Never commit secrets to version control"
echo -e "- Rotate secrets regularly (especially after team changes)"
echo -e "- Self-signed certificate will show browser warning (expected)"
echo -e "- Renew certificate annually: ${YELLOW}./scripts/renew-cert.sh${NC}\n"
