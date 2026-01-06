# DHCP Admin - Bezpečnostná dokumentácia

## Prehľad bezpečnostných opatrení

Táto aplikácia implementuje viacvrstvovú bezpečnosť pre ochranu pred kybernetickými hrozbami.

## 🛡️ Implementované bezpečnostné funkcie

### 1. Autentifikácia & Autorizácia

#### JWT Token Authentication
- **Access token expiration**: 30 minút (konfigurovateľné)
- **Token signing**: HMAC-SHA256 s 64-byte SECRET_KEY
- **Secure password hashing**: bcrypt s cost factor 12+

#### Role-Based Access Control (RBAC)
- **ADMIN**: Plný prístup (user management, settings)
- **RW** (Read-Write): Úprava zariadení, IP rozsahov, DHCP konfigurácie
- **RO** (Read-Only): Iba čítanie dát

### 2. Rate Limiting

#### Ochrana proti brute force
- **Login endpoint**: 5 pokusov/minútu na IP adresu
- **General endpoints**: 100 požiadaviek/minútu na IP adresu
- **Hourly limit**: 1000 požiadaviek/hodinu na IP adresu

### 3. Security Headers

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### 4. Input Validation

#### Hostname
- Regex: `^[a-zA-Z0-9_-]+$`
- Max length: 63 znakov
- Žiadna diakritika, medzery, špeciálne znaky

#### MAC Address
- Formát: `XX:XX:XX:XX:XX:XX`
- Normalizácia a validácia
- Kontrola unikátnosti

#### IP Address
- IPv4 validácia
- Kontrola príslušnosti do rozsahu
- Kontrola unikátnosti

### 5. Docker Security

#### Non-root Execution
- Kontajnery bežia ako user `1000:1000`
- Žiadne root privileges

#### Capability Dropping
```yaml
cap_drop:
  - ALL
cap_add:
  - NET_BIND_SERVICE  # Iba pre port 514
```

#### Read-only Filesystem
- Root filesystem je read-only
- Writable iba potrebné volumes

#### Resource Limits
```yaml
limits:
  cpus: '2.0'
  memory: 1G
reservations:
  cpus: '0.5'
  memory: 256M
```

#### Security Options
```yaml
security_opt:
  - no-new-privileges:true
```

### 6. Network Security

#### Network Isolation
- Vlastná Docker network
- Interná komunikácia medzi kontajnermi
- Backend API dostupný len cez nginx reverse proxy

#### HTTPS/TLS
- TLS 1.2 a TLS 1.3
- Strong cipher suites (ECDHE)
- OCSP stapling
- HTTP Strict Transport Security (HSTS)

#### Port Binding
- Backend bind na `127.0.0.1:8002` (localhost only)
- Nginx ako jediný verejný endpoint

### 7. Secrets Management

#### Docker Secrets
```yaml
secrets:
  - secret_key        # JWT signing key
  - admin_username    # Admin credentials
  - admin_password
  - admin_email
```

#### Environment Variables
- **Nepoužívať** pre hesla a tajné kľúče!
- Používať Docker secrets alebo externe vault (HashiCorp Vault, AWS Secrets Manager)

### 8. Logging & Monitoring

#### Log Rotation
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

#### Security Events
- Failed login attempts
- Rate limit violations
- Permission denied events

### 9. Database Security

#### SQLite Configuration
- Database súbor s `chmod 600`
- Žiadny remote prístup
- Automatic backups (odporúčané)

#### SQL Injection Protection
- SQLAlchemy ORM
- Parametrizované queries
- Input validation

### 10. CORS Policy

```python
CORS_ORIGINS=https://yourdomain.com
```
- **Nikdy** nepoužívať `*` v produkcii!
- Povoliť iba dôveryhodné domény

## 🚨 Bezpečnostné odporúčania

### Pre produkciu

#### 1. SSL/TLS Certifikát
```bash
# Self-signed certifikát (automaticky vytvorený)
# Obnovenie raz ročne:
./scripts/renew-cert.sh
docker compose -f docker-compose.prod.yml restart nginx
```

#### 2. Silné heslá
- Minimálne 12 znakov
- Kombinácia písmen, čísiel, symbolov
- Použiť generátor hesiel

#### 3. Secrets Rotation
```bash
# Každých 90 dní
./scripts/rotate-secrets.sh
```

#### 4. Firewall Rules
```bash
# Povoliť len potrebné porty
ufw allow 80/tcp    # HTTP (redirect to HTTPS)
ufw allow 443/tcp   # HTTPS
ufw allow 514/udp   # Syslog (len z DHCP servera)
ufw enable
```

#### 5. Regular Updates
```bash
# Update Docker images
docker compose pull
docker compose up -d

# Update system packages
apt update && apt upgrade -y
```

#### 6. Backup Strategy
```bash
# Daily backup
0 2 * * * /usr/local/bin/backup-dhcp-admin.sh
```

#### 7. Monitoring
- Sledovať failed login attempts
- Monitorovať resource usage
- Alerting pre security events

## 🔐 Checklist pre deployment

- [ ] Vygenerované silné SECRET_KEY (64+ znakov)
- [ ] Admin heslo zmenené z default
- [ ] CORS_ORIGINS nastavené na produkčnú doménu
- [ ] SSL/TLS certifikát nainštalovaný
- [ ] Docker secrets nakonfigurované
- [ ] Firewall pravidlá aktivované
- [ ] Logging nakonfigurovaný
- [ ] Backup plán nastavený
- [ ] Health checks fungujú
- [ ] Rate limiting otestovaný
- [ ] `/api/docs` vypnuté (DEBUG=false)

## 🐛 Vulnerability Reporting

Ak nájdete bezpečnostnú chybu:
1. **NEPUBLIKUJTE** ju verejne
2. Kontaktujte: security@yourdomain.com
3. Poskytnite detaily a PoC

## 📋 Compliance

- **GDPR**: Uchovávanie logov max 6 mesiacov
- **OWASP Top 10**: Ochrana implementovaná
- **CIS Docker Benchmark**: Dodržané best practices

## 🔄 Security Audit Log

| Dátum | Verzia | Audit | Zistenia |
|-------|--------|-------|----------|
| 2026-01-06 | 1.0.0 | Initial | Bezpečnostné features implementované |

## 📚 Ďalšie zdroje

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OpenSSL Documentation](https://www.openssl.org/docs/)

## 📞 Kontakt

Pre bezpečnostné otázky: security@yourdomain.com
