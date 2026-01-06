# DHCP Admin - Quick Start Guide

## 🚀 Rýchle spustenie v produkcii (5 minút)

### 1. Inicializácia

```bash
cd /home/matoh12/dhcp-admin

# Spustiť inicializačný script
./scripts/init-secrets.sh
```

**Čo script urobí:**
- Vygeneruje silný SECRET_KEY (64 bytes)
- Vytvorí admin credentials
- Vygeneruje self-signed SSL certifikát
- Vytvorí `.env.production` súbor

### 2. Konfigurácia (voliteľné)

```bash
# Upraviť CORS origins (ak je to potrebné)
nano .env.production

# Zmeniť:
CORS_ORIGINS=https://192.168.1.100,https://yourserver.local
```

### 3. Spustenie

```bash
# Production deployment
docker compose -f docker-compose.prod.yml up -d

# Kontrola statusu
docker compose -f docker-compose.prod.yml ps

# Sledovať logy
docker compose -f docker-compose.prod.yml logs -f
```

### 4. Prístup

```
HTTPS: https://your-server-ip
Admin username: (zadané pri init-secrets.sh)
Admin password: (zadané pri init-secrets.sh)
```

**⚠️ Poznámka:** Prehliadač zobrazí upozornenie o self-signed certifikáte - to je normálne. Klikni "Pokračovať" alebo "Accept Risk".

---

## 📋 Development (localhost)

Pre vývoj môžeš použiť štandardný docker-compose:

```bash
# Development mode
docker compose up -d

# Prístup
http://localhost:3002

# Default credentials
Username: admin
Password: AdminDHCP2026!
```

---

## 🔧 Základná údržba

### Backup databázy
```bash
docker cp dhcp-admin-backend:/app/data/dhcp-admin.db backup-$(date +%Y%m%d).db
```

### Sledovanie logov
```bash
docker compose -f docker-compose.prod.yml logs -f backend
```

### Reštart služieb
```bash
docker compose -f docker-compose.prod.yml restart
```

### Update aplikácie
```bash
git pull
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

### Obnovenie SSL certifikátu (raz ročne)
```bash
./scripts/renew-cert.sh
docker compose -f docker-compose.prod.yml restart nginx
```

---

## 🛡️ Security Features

✅ **Rate Limiting**
- Login: 5 pokusov/minútu
- API: 100 req/min, 1000 req/hour

✅ **HTTPS/TLS**
- TLS 1.2 + 1.3
- Strong cipher suites

✅ **Security Headers**
- HSTS, XSS Protection, CSP, X-Frame-Options

✅ **Docker Security**
- Non-root containers
- Read-only filesystem
- Capability dropping
- Resource limits

✅ **Authentication**
- JWT tokens (30 min expiry)
- Bcrypt password hashing
- Role-based access (ADMIN/RW/RO)

---

## 📚 Dokumentácia

- **SECURITY.md** - Komplexná bezpečnostná dokumentácia
- **DEPLOYMENT.md** - Detailný deployment guide
- **README.md** - Hlavná dokumentácia projektu

---

## ⚠️ Dôležité

1. **Zálohuj secrets/** - obsahuje kritické kľúče
2. **Nikdy necommituj** secrets/ do gitu
3. **Zmeň admin heslo** po prvom prihlásení
4. **Nastav firewall** (porty 80, 443, 514, 67)
5. **Pravidelné backupy** databázy

---

## 🐛 Troubleshooting

### Backend nenastartuje
```bash
docker logs dhcp-admin-backend
docker compose -f docker-compose.prod.yml restart backend
```

### Zabudnuté admin heslo
```bash
# Resetovať secrets
rm -rf secrets/
./scripts/init-secrets.sh
docker compose -f docker-compose.prod.yml restart
```

### SSL certificate error
```bash
# Obnoviť certifikát
./scripts/renew-cert.sh
docker compose -f docker-compose.prod.yml restart nginx
```

### Porty už používané
```bash
# Zmeniť porty v docker-compose.prod.yml
ports:
  - "8080:80"   # namiesto 80
  - "8443:443"  # namiesto 443
```

---

## 📞 Support

Pre problémy alebo otázky:
- Skontroluj logs: `docker compose logs`
- Review dokumentáciu: `SECURITY.md`, `DEPLOYMENT.md`
- GitHub Issues (ak je projekt na GitHube)

---

**Hotovo! Aplikácia je zabezpečená a ready to use! 🎉**
