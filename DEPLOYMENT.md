## DHCP Admin - Production Deployment Guide

## 📋 Požiadavky

- Docker 20.10+
- Docker Compose 2.0+
- Linux server (Ubuntu 20.04+ / Debian 11+)
- Minimálne 2GB RAM, 2 CPU cores
- 20GB disk space

## 🚀 Rýchly štart - Produkčné nasadenie

### 1. Inicializácia secrets

```bash
# Spustiť script pre vytvorenie secrets
./scripts/init-secrets.sh
```

Script vytvorí:
- `secrets/` adresár s JWT kľúčmi a admin credentials
- `nginx/ssl/` s self-signed certifikátom (pre development)
- `.env.production` súbor

### 2. Konfigurácia

#### A. Upraviť `.env.production`

```bash
nano .env.production
```

Zmeniť:
```env
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### B. Upraviť `docker-compose.prod.yml`

Pre DHCP server na host network (produkcia):
```yaml
dhcp-server:
  # Uncomment this:
  network_mode: host
```

### 3. SSL Certifikát

Self-signed certifikát sa vytvorí automaticky pri `init-secrets.sh`.

#### Obnovenie certifikátu (raz ročne)

```bash
./scripts/renew-cert.sh
docker compose -f docker-compose.prod.yml restart nginx
```

#### Vlastný certifikát (voliteľné)

```bash
# Nahradiť self-signed certifikát vlastným
cp your-cert.pem nginx/ssl/cert.pem
cp your-key.pem nginx/ssl/key.pem
chmod 600 nginx/ssl/key.pem
docker compose -f docker-compose.prod.yml restart nginx
```

### 4. Firewall

```bash
# UFW
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw allow 514/udp comment 'Syslog'
ufw allow 67/udp comment 'DHCP'
ufw enable

# Alebo iptables
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -p udp --dport 514 -j ACCEPT
iptables -A INPUT -p udp --dport 67 -j ACCEPT
iptables-save > /etc/iptables/rules.v4
```

### 5. Spustenie aplikácie

```bash
# Production deployment
docker compose -f docker-compose.prod.yml up -d

# Kontrola logov
docker compose -f docker-compose.prod.yml logs -f

# Kontrola stavu
docker compose -f docker-compose.prod.yml ps
```

### 6. Verifikácia

```bash
# Health check
curl https://yourdomain.com/health

# API test
curl https://yourdomain.com/api/v1/

# SSL test
curl -I https://yourdomain.com
```

## 🔧 Údržba

### Backup

```bash
#!/bin/bash
# backup-dhcp-admin.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/dhcp-admin"

mkdir -p $BACKUP_DIR

# Backup databázy
docker cp dhcp-admin-backend:/app/data/dhcp-admin.db \
  $BACKUP_DIR/dhcp-admin-$DATE.db

# Backup DHCP konfigurácie
docker cp dhcp-admin-backend:/dhcp-config/dhcpd.conf \
  $BACKUP_DIR/dhcpd-$DATE.conf

# Kompresia
tar czf $BACKUP_DIR/backup-$DATE.tar.gz \
  $BACKUP_DIR/*-$DATE.*

# Vymazať staré backupy (> 30 dní)
find $BACKUP_DIR -name "backup-*.tar.gz" -mtime +30 -delete

echo "✓ Backup completed: $BACKUP_DIR/backup-$DATE.tar.gz"
```

### Update aplikácie

```bash
# Pull najnovšie zmeny
git pull origin main

# Rebuild kontajnerov
docker compose -f docker-compose.prod.yml build

# Reštart s novými images
docker compose -f docker-compose.prod.yml up -d

# Cleanup starých images
docker image prune -f
```

### Monitorovanie

```bash
# Sledovať logy v reálnom čase
docker compose -f docker-compose.prod.yml logs -f backend

# Resource usage
docker stats

# Health checks
watch -n 30 'curl -s https://yourdomain.com/health | jq'
```

### Rotate Secrets

```bash
# Každých 90 dní
./scripts/rotate-secrets.sh

# Reštart s novými secrets
docker compose -f docker-compose.prod.yml restart
```

## 📊 Performance Tuning

### Database Optimization

```bash
# Pravidelná údržba SQLite
docker exec dhcp-admin-backend sqlite3 /app/data/dhcp-admin.db "VACUUM;"
docker exec dhcp-admin-backend sqlite3 /app/data/dhcp-admin.db "ANALYZE;"
```

### Log Retention

V Settings UI:
- Syslog retention: 90-180 dní (odporúčané)
- Cleanup hour: 2:00 (nízka záťaž)

## 🐛 Troubleshooting

### Backend nenastartuje

```bash
# Kontrola logov
docker logs dhcp-admin-backend

# Kontrola permissions
ls -la data/ dhcp-config/

# Fix permissions
chown -R 1000:1000 data/ dhcp-config/
```

### DHCP server restart loop

```bash
# Pre host network mode
docker compose -f docker-compose.prod.yml stop dhcp-server
docker compose -f docker-compose.prod.yml up -d dhcp-server

# Kontrola konfigurácie
docker exec dhcp-admin-dhcp-server cat /dhcp-config/dhcpd.conf
```

### SSL certificate errors

```bash
# Kontrola certifikátu
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Renewal Let's Encrypt
certbot renew --force-renewal
```

### Rate limiting príliš prísny

Upraviť `backend/app/middleware/security.py`:
```python
# Zvýšiť limity
if len(self.requests[client_ip]) >= 200:  # z 100
```

## 📞 Support

- GitHub Issues: https://github.com/yourusername/dhcp-admin/issues
- Security: security@yourdomain.com
- Documentation: https://docs.yourdomain.com

## 📝 Changelog

### v1.0.0 (2026-01-06)
- Initial production release
- Security hardening
- Docker secrets support
- HTTPS/TLS support
- Rate limiting
- RBAC implementation
