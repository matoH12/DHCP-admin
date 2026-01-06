# DHCP Admin Panel

A modern web-based management interface for ISC DHCP Server with authentication, device management, IP range configuration, and automatic DHCP configuration generation.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![React](https://img.shields.io/badge/React-18+-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

## ✨ Features

### Core Functionality
- 🔐 **Secure Authentication** - JWT tokens with bcrypt password hashing
- 📋 **Device Management** - Full CRUD operations for DHCP static host reservations
- 🌐 **IP Range Management** - Define networks with CIDR notation and dynamic pools
- 🔍 **Advanced Search** - Intuitive search across hostname, MAC address, and IP
- 📊 **Analytics Dashboard** - Interactive charts with Recharts showing IP utilization, device activity, DHCP events, and top active devices
- 📈 **Device Activity Tracking** - Historical device activity tracking with 90-day retention
- 📄 **DHCP Config Generation** - Automatic generation of ISC DHCP compatible `dhcpd.conf`
- 👥 **User Management** - Role-based access control (Admin, Read-Write, Read-Only)
- 📡 **Syslog Server** - Built-in syslog server for DHCP log collection and analysis
- ⏱️ **Last Seen Tracking** - Monitor device activity based on DHCP logs
- 📚 **API Documentation** - Swagger UI and ReDoc accessible from Settings page (protected by authentication)
- ✅ **Comprehensive Validation** - Hostname, MAC address, and IP address validation

### Security Features
- 🔒 **Rate Limiting** - Protection against brute force attacks
- 🛡️ **Security Headers** - HSTS, CSP, X-Frame-Options, and more
- 🔐 **HTTPS Support** - Self-signed, Let's Encrypt, or custom certificates
- 🌐 **Flexible CORS** - Configurable cross-origin resource sharing
- 🐳 **Hardened Docker** - Non-root containers with capability dropping

### Deployment Options
- 🚀 **Production Deployment** - Full security with Let's Encrypt SSL
- 🏢 **Internal Network** - Self-signed certificate deployment
- 🔄 **Behind Proxy** - HTTP-only mode for reverse proxy setups
- 💻 **Development Mode** - Quick setup for local development

## 📋 Table of Contents

- [Technology Stack](#-technology-stack)
- [Quick Start](#-quick-start)
- [Deployment Scenarios](#-deployment-scenarios)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Security](#-security)
- [Maintenance](#-maintenance)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🛠 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework with automatic API documentation
- **SQLAlchemy** - SQL toolkit and ORM
- **Alembic** - Database migration tool
- **SQLite** - Lightweight file-based database
- **JWT** - JSON Web Tokens for secure authentication
- **Bcrypt** - Industry-standard password hashing
- **Uvicorn** - Lightning-fast ASGI server

### Frontend
- **React 18** - Modern UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Next generation frontend tooling
- **Ant Design** - Enterprise-grade UI components
- **Recharts** - Composable charting library for analytics visualizations
- **Axios** - Promise-based HTTP client
- **Day.js** - Lightweight date library with Slovak locale support

### Infrastructure
- **Docker & Docker Compose** - Containerized deployment
- **Nginx** - Reverse proxy and SSL termination
- **ISC DHCP Server 4.4** - Industry-standard DHCP server
- **Rsyslog** - Reliable syslog processing

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- OR Python 3.11+ and Node.js 18+ for local development

### Option 1: Simple Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/matoH12/DHCP-admin.git
cd DHCP-admin
```

2. **Start the application**
```bash
docker compose up -d
```

3. **Access the application**
- Frontend: http://localhost:3003
- Backend API: Not exposed externally (security hardening)
- API accessible via frontend proxy at http://localhost:3003/api

4. **Default credentials**
```
Username: admin
Password: AdminDHCP2026!
Email: admin@example.com
```

### 🔄 Database Reset (If Login Fails)

If you're getting 401 Unauthorized errors when trying to login, you may need to reset the database:

```bash
# 1. Stop containers
docker compose down

# 2. Delete old database
rm -f data/dhcp-admin.db

# 3. Start fresh (creates new database with current password)
docker compose up -d

# 4. Wait for initialization
sleep 10

# 5. Verify admin user was created
docker compose logs backend | grep "Admin user"
```

You should see: `✓ Admin user 'admin' ready`

Now login with the credentials above.

### 📁 Directory Structure

The application automatically creates these directories on first clone (tracked via `.gitkeep`):

```
dhcp-admin/
├── data/              # SQLite database (auto-created on first run)
├── dhcp-config/       # Generated DHCP configuration files
├── dhcp-logs/         # DHCP server logs (viewable in web UI)
├── dhcp-leases/       # DHCP lease database
├── backend/           # FastAPI backend application
├── frontend/          # React frontend application
└── dhcp-server/       # ISC DHCP server container config
```

**No manual directory creation needed!** All directories are automatically created when you clone the repository.

### Option 2: Production Deployment

For production deployment with full security features, follow the [Flexible Deployment Guide](FLEXIBLE-DEPLOYMENT.md).

**Quick production setup:**

```bash
# 1. Run configuration wizard
./scripts/configure-deployment.sh

# 2. Initialize secrets
./scripts/init-secrets.sh

# 3. Optional: Setup Let's Encrypt
./scripts/setup-letsencrypt.sh yourdomain.com

# 4. Start deployment
./scripts/start-deployment.sh
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 📦 Deployment Scenarios

### 1. Production with Let's Encrypt
```bash
./scripts/configure-deployment.sh
# Select: SSL = Let's Encrypt
#         CORS = Enabled
#         Security = All enabled

./scripts/setup-letsencrypt.sh yourdomain.com admin@yourdomain.com
./scripts/start-deployment.sh
```

**Features:**
- ✅ Valid SSL certificate (90 days, auto-renewal)
- ✅ HTTPS on port 443
- ✅ Rate limiting + Security headers
- ✅ CORS for your domain

### 2. Internal Network (Self-signed)
```bash
./scripts/configure-deployment.sh
# Select: SSL = Self-signed
#         CORS = Enabled
#         Security = All enabled

./scripts/init-secrets.sh
./scripts/start-deployment.sh
```

**Features:**
- ✅ Self-signed SSL (365 days)
- ✅ HTTPS on port 443 (browser warning expected)
- ✅ Rate limiting + Security headers
- ✅ CORS for internal addresses

### 3. Behind HTTPS Proxy
```bash
./scripts/configure-deployment.sh
# Select: SSL = HTTP only
#         CORS = Optional
#         Security = Optional

./scripts/init-secrets.sh --no-ssl
./scripts/start-deployment.sh
```

**Features:**
- ✅ HTTP on port 80
- ✅ No SSL overhead (proxy handles it)
- ⚙️ CORS/Security as configured
- ✅ Trust X-Forwarded-* headers

### 4. Development Mode
```bash
docker compose up -d
```

Access: http://localhost:3003

## 📚 API Documentation

### Interactive Documentation

Access API documentation directly from the web interface:

1. **Login** to the application at http://localhost:3003
2. **Navigate** to Settings (Nastavenia)
3. **Click** on API Documentation cards:
   - **Swagger UI** - Interactive API testing with request/response examples
   - **ReDoc** - Clean, readable API documentation

The documentation is **protected by authentication** - your JWT token is automatically included when you open it from the Settings page.

**Alternative access** (requires manual token):
- Swagger UI: http://localhost:3003/api/docs (with Authorization header)
- ReDoc: http://localhost:3003/api/redoc (with Authorization header)

### Authentication

**Login**
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "AdminDHCP2026!"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - User logout

#### User Management
- `GET /api/v1/users/` - List all users
- `POST /api/v1/users/` - Create new user
- `PUT /api/v1/users/{id}/` - Update user
- `DELETE /api/v1/users/{id}/` - Delete user

**User Roles:**
- `ADMIN` - Full access (user management, all operations)
- `RW` - Read-Write access (manage devices and ranges)
- `RO` - Read-Only access (view only)

#### IP Ranges
- `GET /api/v1/ranges/` - List IP ranges
- `POST /api/v1/ranges/` - Create IP range
- `PUT /api/v1/ranges/{id}` - Update IP range
- `DELETE /api/v1/ranges/{id}` - Delete IP range
- `GET /api/v1/ranges/{id}/stats` - Get range statistics
- `GET /api/v1/ranges/{id}/available-ips` - List available IPs

#### Devices
- `GET /api/v1/devices/` - List devices (with search)
- `POST /api/v1/devices/` - Create device
- `PUT /api/v1/devices/{id}` - Update device
- `DELETE /api/v1/devices/{id}` - Delete device
- `GET /api/v1/devices/suggest-ip/{range_id}` - Suggest available IP

#### DHCP Configuration
- `POST /api/v1/dhcp/generate` - Generate DHCP config
- `GET /api/v1/dhcp/preview` - Preview configuration
- `GET /api/v1/dhcp/active` - Get active config
- `GET /api/v1/dhcp/download` - Download config file
- `GET /api/v1/dhcp/history` - Configuration history

#### Syslog
- `GET /api/v1/syslog/` - List syslog messages
- `GET /api/v1/syslog/stats` - Syslog statistics
- `GET /api/v1/syslog/count` - Message count
- `DELETE /api/v1/syslog/bulk` - Delete old logs

#### Statistics & Analytics
- `GET /api/v1/stats/overview` - System overview with chart data
- `GET /api/v1/stats/devices-by-range` - Devices per range
- `GET /api/v1/stats/recent-devices` - Recently added devices
- `GET /api/v1/stats/device-activity-timeline` - Daily device activity for charts (7-90 days)
- `GET /api/v1/stats/dhcp-events` - DHCP event distribution for pie charts (1-168 hours)
- `GET /api/v1/stats/top-active-devices` - Most active devices ranking (5-50 devices, 1-30 days)

### Example: Creating an IP Range

```bash
curl -X POST "http://localhost:8002/api/v1/ranges/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Office Network",
    "network_address": "192.168.1.0",
    "cidr": 24,
    "gateway": "192.168.1.1",
    "dns_servers": ["8.8.8.8", "8.8.4.4"],
    "domain_name": "office.local",
    "pool_start": "192.168.1.100",
    "pool_end": "192.168.1.200",
    "description": "Main office network"
  }'
```

### Example: Adding a Device

```bash
curl -X POST "http://localhost:8002/api/v1/devices/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "printer-hp",
    "mac_address": "00:11:22:33:44:55",
    "ip_address": "192.168.1.10",
    "ip_range_id": 1,
    "description": "HP LaserJet Printer"
  }'
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Application
APP_NAME=DHCP Admin
DEBUG=false

# Database
DATABASE_URL=sqlite:///./data/dhcp-admin.db

# Security
SECRET_KEY=your-secret-key-here-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3003

# DHCP Configuration
DHCP_CONFIG_PATH=/dhcp-config/dhcpd.conf

# Admin User (change these!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-password
ADMIN_EMAIL=admin@localhost

# Security Features (optional)
ENABLE_CORS=true
ENABLE_RATE_LIMITING=true
ENABLE_SECURITY_HEADERS=true
```

### Generate Secure SECRET_KEY

```bash
openssl rand -hex 32
```

### Flexible Security Configuration

You can enable/disable security features using environment variables:

```bash
# Enable all security features (recommended)
ENABLE_CORS=true
ENABLE_RATE_LIMITING=true
ENABLE_SECURITY_HEADERS=true

# Disable for deployment behind trusted proxy
ENABLE_CORS=false
ENABLE_RATE_LIMITING=false
ENABLE_SECURITY_HEADERS=false
```

## 🔒 Security

### Production Security Checklist

- [ ] Change default admin password
- [ ] Generate strong SECRET_KEY
- [ ] Configure HTTPS with valid certificate
- [ ] Set CORS_ORIGINS to your specific domain(s)
- [ ] Enable rate limiting
- [ ] Enable security headers
- [ ] Disable API docs in production (DEBUG=false)
- [ ] Configure firewall rules
- [ ] Secure the secrets/ directory (chmod 700)
- [ ] Regular backups
- [ ] Monitor logs for suspicious activity

### Rate Limiting

Default rate limits:
- **Login endpoint**: 5 attempts per minute
- **API endpoints**: 100 requests per minute
- **Hourly limit**: 1000 requests per hour

### Security Headers

When `ENABLE_SECURITY_HEADERS=true`:
- Strict-Transport-Security (HSTS)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection
- Content-Security-Policy
- Referrer-Policy
- Permissions-Policy

### SSL/TLS Options

1. **Let's Encrypt** - Free, auto-renewing certificates
2. **Self-signed** - For internal networks
3. **Custom** - Bring your own certificate
4. **HTTP-only** - For deployment behind HTTPS proxy

See [FLEXIBLE-DEPLOYMENT.md](FLEXIBLE-DEPLOYMENT.md) for setup instructions.

## 🗃 Database Schema

### User
```sql
- id: INTEGER PRIMARY KEY
- username: VARCHAR(50) UNIQUE
- email: VARCHAR(255) UNIQUE
- hashed_password: VARCHAR(255)
- role: VARCHAR(20) (ADMIN, RW, RO)
- is_active: BOOLEAN
- created_at: DATETIME
- updated_at: DATETIME
```

### IPRange
```sql
- id: INTEGER PRIMARY KEY
- name: VARCHAR(100)
- network_address: VARCHAR(15)
- cidr: INTEGER
- gateway: VARCHAR(15)
- dns_servers: JSON
- domain_name: VARCHAR(255)
- pool_start: VARCHAR(15)
- pool_end: VARCHAR(15)
- description: TEXT
- is_active: BOOLEAN
- created_at: DATETIME
- updated_at: DATETIME
```

### Device
```sql
- id: INTEGER PRIMARY KEY
- hostname: VARCHAR(63) UNIQUE
- mac_address: VARCHAR(17) UNIQUE
- ip_address: VARCHAR(15) UNIQUE
- ip_range_id: INTEGER FOREIGN KEY
- description: TEXT
- is_active: BOOLEAN
- created_at: DATETIME
- updated_at: DATETIME
- created_by: INTEGER FOREIGN KEY
```

### DHCPConfig
```sql
- id: INTEGER PRIMARY KEY
- version: INTEGER
- config_content: TEXT
- file_path: VARCHAR(255)
- generated_at: DATETIME
- generated_by: INTEGER FOREIGN KEY
- is_active: BOOLEAN
```

### SyslogMessage
```sql
- id: INTEGER PRIMARY KEY
- timestamp: DATETIME
- hostname: VARCHAR(255)
- program: VARCHAR(100)
- severity: VARCHAR(20)
- facility: VARCHAR(20)
- message: TEXT
- raw_message: TEXT
- source_ip: VARCHAR(15)
- created_at: DATETIME
```

### DeviceHistory
```sql
- id: INTEGER PRIMARY KEY
- device_id: INTEGER FOREIGN KEY
- timestamp: DATETIME (indexed)
- ip_address: VARCHAR(15)
- mac_address: VARCHAR(17)
- event_type: VARCHAR(20) (ACK, REQUEST, etc.)
- is_active: BOOLEAN
```

### Settings
```sql
- key: VARCHAR(100) PRIMARY KEY
- value: TEXT
- description: TEXT
```

## 📊 Dashboard Analytics

The dashboard features **4 interactive charts** powered by Recharts:

### 1. IP Utilization Bar Chart
- **Stacked bar chart** showing assigned vs available IPs per range
- **Color-coded**: Blue (assigned), Green (available)
- **Custom tooltips** with utilization percentage
- Updates in real-time with data changes

### 2. Device Activity Timeline
- **Area chart** showing daily device activity over time
- **Period selector**: 7 or 30 days
- **Metrics**: Active devices and total DHCP events per day
- **Auto-refresh**: Updates every 60 seconds
- Data from `DeviceHistory` table

### 3. DHCP Events Pie Chart
- **Pie chart** showing distribution of DHCP event types
- **Event types**: DISCOVER, OFFER, REQUEST, ACK, NAK, RELEASE
- **Time range**: Last 24 hours
- **Color-coded** by event type
- Data parsed from syslog messages

### 4. Top Active Devices List
- **Ranked list** of most active devices (7 days)
- **Shows**: Hostname, IP, MAC, activity count, last seen
- **Visual ranking**: Top 3 highlighted in green
- **Relative timestamps** in Slovak locale

### Device History Tracking

**Automatic Activity Recording:**
- Every DHCP ACK/REQUEST event creates a `DeviceHistory` record
- Tracks: device_id, timestamp, IP, MAC, event_type
- **90-day retention** with automatic cleanup
- **Optimized queries** with composite indexes

**Use Cases:**
- Identify most/least active devices
- Track device activity patterns
- Historical presence analysis
- Network usage trends

## 📝 Generated DHCP Configuration

Example of generated `dhcpd.conf`:

```conf
# DHCP Configuration File
# Generated by DHCP Admin Panel
# Generated at: 2026-01-06 12:00:00 UTC
#
# WARNING: This file is auto-generated. Manual changes will be overwritten.

# Global DHCP Options
default-lease-time 600;
max-lease-time 7200;
authoritative;
log-facility local7;

# Subnet: Office Network
subnet 192.168.1.0 netmask 255.255.255.0 {
    option routers 192.168.1.1;
    option domain-name-servers 8.8.8.8, 8.8.4.4;
    option domain-name "office.local";

    # Dynamic IP Pool
    pool {
        range 192.168.1.100 192.168.1.200;
    }

    # Static Host Reservations
    host printer-hp {
        hardware ethernet 00:11:22:33:44:55;
        fixed-address 192.168.1.10;
    }

    host server-web {
        hardware ethernet aa:bb:cc:dd:ee:ff;
        fixed-address 192.168.1.20;
    }
}
```

## 🔧 Maintenance

### Backup

**Database:**
```bash
docker compose exec backend cp /app/data/dhcp-admin.db /app/data/dhcp-admin.db.backup
docker compose cp backend:/app/data/dhcp-admin.db.backup ./backup/
```

**DHCP Configuration:**
```bash
cp dhcp-config/dhcpd.conf backup/dhcpd.conf.$(date +%Y%m%d)
```

### Logs

**View all logs:**
```bash
docker compose -f docker-compose.prod.yml logs -f
```

**Backend only:**
```bash
docker compose -f docker-compose.prod.yml logs -f backend
```

**Check security features:**
```bash
docker compose logs backend | grep -E "CORS|Rate|Security"
```

### Updates

```bash
git pull
docker compose build
docker compose up -d
```

### Certificate Renewal

**Self-signed (annual):**
```bash
./scripts/renew-cert.sh
docker compose -f docker-compose.prod.yml restart nginx
```

**Let's Encrypt (automatic):**
```bash
certbot renew
docker compose -f docker-compose.prod.yml restart nginx
```

### Cleanup Old Syslog Messages

Via API:
```bash
curl -X DELETE "http://localhost:8002/api/v1/syslog/bulk?days=180" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Or configure automatic cleanup in settings (default: 180 days).

## 💻 Development

### Local Development Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
cd backend
pytest
pytest --cov=app tests/
```

### Database Migrations

**Create migration:**
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

**Apply migration:**
```bash
alembic upgrade head
```

**Rollback:**
```bash
alembic downgrade -1
```

### Code Quality

```bash
# Backend linting
cd backend
flake8 app/
black app/
mypy app/

# Frontend linting
cd frontend
npm run lint
npm run type-check
```

## 🐛 Troubleshooting

### Backend won't start

**Check logs:**
```bash
docker compose logs backend
```

**Common issues:**
- Database file permissions
- Missing SECRET_KEY
- Port already in use

**Solution:**
```bash
chmod 777 data/
docker compose down && docker compose up -d
```

### Can't login

1. Check admin credentials in `.env`
2. Verify backend is running: `docker compose ps`
3. Check logs: `docker compose logs backend | grep -i error`
4. Reset admin password:
```bash
docker compose exec backend python -c "
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash
db = SessionLocal()
admin = db.query(User).filter(User.username == 'admin').first()
admin.hashed_password = get_password_hash('new-password')
db.commit()
"
```

### DHCP config not generating

1. Check permissions: `ls -la dhcp-config/`
2. Check logs for errors: `docker compose logs backend | grep -i dhcp`
3. Verify devices and ranges exist
4. Test API endpoint: `curl -X POST http://localhost:8002/api/v1/dhcp/generate -H "Authorization: Bearer TOKEN"`

### Frontend can't connect to backend

1. Check CORS settings in `.env`
2. Verify backend is accessible: `curl http://localhost:8002/health`
3. Check browser console for errors
4. Verify API_URL in frontend config

### Rate limiting too strict

Temporarily disable:
```bash
# In .env
ENABLE_RATE_LIMITING=false

# Restart
docker compose restart backend
```

Or adjust limits in `backend/app/middleware/security.py`.

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for all frontend code
- Write tests for new features
- Update documentation
- Follow conventional commits

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- React and Ant Design for the frontend
- ISC for the DHCP server software
- The open source community

## 📧 Support

- **Issues**: https://github.com/matoH12/DHCP-admin/issues
- **Documentation**: See documentation files in the repository
- **Questions**: Open an issue with the question label

## 🗺️ Roadmap

### Completed ✅
- [x] Dashboard analytics with interactive charts (Recharts)
- [x] Device activity history tracking
- [x] DHCP event analysis from syslog
- [x] Protected API documentation (Swagger/ReDoc)
- [x] Automatic syslog cleanup with configurable retention

### Planned Features
- [ ] IPv6 support
- [ ] Multi-server management
- [ ] DHCP failover configuration
- [ ] Email notifications for critical events
- [ ] LDAP/Active Directory integration
- [ ] REST API webhook support
- [ ] Export reports (PDF, CSV)
- [ ] Network topology visualization
- [ ] Advanced alerting system
- [ ] Backup/restore functionality

---

**Made with ❤️ using FastAPI, React, and Docker**
