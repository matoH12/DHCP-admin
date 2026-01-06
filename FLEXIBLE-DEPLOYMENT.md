# DHCP Admin - Flexibilný Deployment Guide

## 🎯 Prehľad

Aplikácia podporuje rôzne deployment scenáre s flexibilnou konfiguráciou:

| Scenár | SSL | CORS | Security | Use Case |
|--------|-----|------|----------|----------|
| **Production** | Let's Encrypt | Enabled | Full | Verejný server |
| **Internal** | Self-signed | Enabled | Full | Interná sieť |
| **Behind Proxy** | HTTP only | Optional | Optional | Za HTTPS proxy/LB |
| **Development** | Self-signed | Enabled | Full | Localhost test |

## 🚀 Quick Start - Interaktívny Wizard

### Krok 1: Spusti konfiguračný wizard

```bash
cd /home/matoh12/dhcp-admin
./scripts/configure-deployment.sh
```

**Wizard sa opýta:**
1. ⚙️ **SSL/TLS typ** (self-signed / Let's Encrypt / vlastný / HTTP only)
2. 🌐 **CORS** (zapnúť/vypnúť + origins)
3. 🛡️ **Security features** (rate limiting, security headers)
4. 📡 **DHCP network mode** (bridge / host)
5. 🌍 **Domain/hostname**

### Krok 2: Inicializuj secrets

```bash
# Pre SSL (self-signed alebo Let's Encrypt)
./scripts/init-secrets.sh

# Pre HTTP only (bez SSL)
./scripts/init-secrets.sh --no-ssl
```

### Krok 3: SSL setup (ak potrebuješ Let's Encrypt)

```bash
./scripts/setup-letsencrypt.sh yourdomain.com
```

### Krok 4: Spusti aplikáciu

```bash
./scripts/start-deployment.sh
```

---

## 📋 Deployment Scenáre

### Scenár 1: Production s Let's Encrypt

**Použitie:** Verejný DHCP admin server s vlastnou doménou

```bash
# 1. Konfigurácia
./scripts/configure-deployment.sh
# Vyber: SSL = Let's Encrypt
#        CORS = Enabled (tvoja doména)
#        Security = All enabled
#        DHCP = Host mode

# 2. Secrets
./scripts/init-secrets.sh

# 3. Let's Encrypt
./scripts/setup-letsencrypt.sh dhcp.example.com admin@example.com

# 4. Start
./scripts/start-deployment.sh
```

**Výsledok:**
- ✅ Platný SSL certifikát (90 dní, auto-renewal)
- ✅ HTTPS na porte 443
- ✅ Rate limiting + Security headers
- ✅ CORS pre tvoju doménu

---

### Scenár 2: Interná sieť (Self-signed)

**Použitie:** DHCP admin v internej/office sieti

```bash
# 1. Konfigurácia
./scripts/configure-deployment.sh
# Vyber: SSL = Self-signed
#        CORS = Enabled (interné IP/hostname)
#        Security = All enabled
#        DHCP = Host mode

# 2. Setup (vytvorí aj self-signed cert)
./scripts/init-secrets.sh

# 3. Start
./scripts/start-deployment.sh
```

**Výsledok:**
- ✅ Self-signed SSL (365 dní)
- ✅ HTTPS na porte 443 (browser warning - expected)
- ✅ Rate limiting + Security headers
- ✅ CORS pre interné adresy

**Renewal (raz ročne):**
```bash
./scripts/renew-cert.sh
docker compose -f docker-compose.prod.yml restart nginx
```

---

### Scenár 3: Za Proxy/Load Balancer

**Použitie:** Aplikácia za nginx/HAProxy/Traefik s HTTPS

```bash
# 1. Konfigurácia
./scripts/configure-deployment.sh
# Vyber: SSL = HTTP only
#        CORS = Optional
#        Security = Optional (proxy môže riešiť)
#        DHCP = Host mode

# 2. Setup (bez SSL)
./scripts/init-secrets.sh --no-ssl

# 3. Start
./scripts/start-deployment.sh
```

**Výsledok:**
- ✅ HTTP na porte 80
- ✅ Žiadny SSL overhead (proxy ho rieši)
- ⚙️ CORS/Security podľa výberu
- ✅ Trust X-Forwarded-* headers

**Proxy konfigurácia (príklad nginx):**
```nginx
server {
    listen 443 ssl http2;
    server_name dhcp.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://dhcp-admin-server:80;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
    }
}
```

---

### Scenár 4: Development/Test

**Použitie:** Localhost vývoj a testovanie

```bash
# Štandardný docker-compose (nie production)
docker compose up -d

# Prístup
http://localhost:3002

# Default credentials
Username: admin
Password: AdminDHCP2026!
```

---

## ⚙️ Environment Variables - Security Features

Môžeš manuálne upraviť `.env.custom` alebo nastaviť v docker-compose:

```bash
# CORS
ENABLE_CORS=true
CORS_ORIGINS=https://admin.example.com,https://example.com

# Security Features
ENABLE_RATE_LIMITING=true
ENABLE_SECURITY_HEADERS=true

# API Docs (development only)
DEBUG=false
```

### Vypnutie všetkých security features (nie odporúčané!)

```bash
ENABLE_CORS=false
ENABLE_RATE_LIMITING=false
ENABLE_SECURITY_HEADERS=false
```

**⚠️ Použiť len za dôveryhodným proxy s vlastným security!**

---

## 🔧 Pokročilá konfigurácia

### Manuálna konfigurácia (bez wizardu)

#### 1. Vytvor `.deployment-config`

```bash
SSL_CHOICE=1                    # 1=self-signed, 2=letsencrypt, 3=custom, 4=none
SSL_TYPE=self-signed
CORS_ENABLED=true
CORS_ORIGINS=https://192.168.1.100
RATE_LIMITING=true
SECURITY_HEADERS=true
API_DOCS=false
DHCP_NETWORK_MODE=host
DOMAIN=dhcp.local
```

#### 2. Vytvor `.env.custom`

```bash
ENABLE_CORS=true
CORS_ORIGINS=https://192.168.1.100
ENABLE_RATE_LIMITING=true
ENABLE_SECURITY_HEADERS=true
DEBUG=false
```

#### 3. Spusti deployment

```bash
./scripts/start-deployment.sh
```

---

## 📊 Comparison Table

| Feature | Production | Internal | Behind Proxy | Development |
|---------|-----------|----------|--------------|-------------|
| SSL Type | Let's Encrypt | Self-signed | None (HTTP) | Self-signed |
| HTTPS | ✅ | ✅ | ❌ (proxy) | ✅ |
| CORS | Strict | Relaxed | Optional | Permissive |
| Rate Limiting | ✅ | ✅ | Optional | ✅ |
| Security Headers | ✅ | ✅ | Optional | ✅ |
| API Docs | ❌ | ❌ | ❌ | ✅ |
| Network Mode | Host | Host | Host | Bridge |

---

## 🛠️ Maintenance

### Kontrola konfigurácie

```bash
cat .deployment-config
cat .env.custom
```

### Zmena konfigurácie

```bash
# Re-run wizard
./scripts/configure-deployment.sh

# Restart s novou konfiguráciou
./scripts/start-deployment.sh
```

### Logs

```bash
# Všetky služby
docker compose -f docker-compose.prod.yml logs -f

# Len backend
docker compose -f docker-compose.prod.yml logs -f backend

# Check security features
docker compose -f docker-compose.prod.yml logs backend | grep -E "CORS|Rate|Security"
```

### Vypnutie/Zapnutie funkcií bez reštartu

Upraviť `.env.custom` a:
```bash
docker compose -f docker-compose.prod.yml restart backend
```

---

## 🔐 Security Best Practices

### Production Checklist

- [ ] Let's Encrypt SSL alebo platný certifikát
- [ ] CORS nastavený len na dôveryhodné domény
- [ ] Rate limiting zapnutý
- [ ] Security headers zapnuté
- [ ] API docs vypnuté (DEBUG=false)
- [ ] Firewall pravidlá aktivované
- [ ] Secrets v bezpečnom adresári (chmod 700)
- [ ] Pravidelné backupy
- [ ] Log monitoring

### Za Proxy Checklist

- [ ] Proxy ma platný SSL certifikát
- [ ] Proxy posiela správne X-Forwarded-* headers
- [ ] Proxy má vlastné rate limiting
- [ ] Backend dostupný len z proxy (firewall)
- [ ] Monitoring proxy logov

---

## 📞 Troubleshooting

### CORS errors

```bash
# Skontroluj nastavenie
cat .env.custom | grep CORS

# Update origins
nano .env.custom
# CORS_ORIGINS=https://new-domain.com

# Restart
docker compose -f docker-compose.prod.yml restart backend
```

### Rate limiting príliš prísny

```bash
# Vypni dočasne
ENABLE_RATE_LIMITING=false

# Alebo uprav limity v backend/app/middleware/security.py
```

### SSL certificate errors

```bash
# Check certifikát
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Renew self-signed
./scripts/renew-cert.sh

# Renew Let's Encrypt
certbot renew
```

---

**Hotovo! Máš flexibilný deployment system pre akýkoľvek use case! 🎉**
