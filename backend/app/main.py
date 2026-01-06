"""
DHCP Admin - Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base
from .middleware import setup_security_middleware

# Import models to create tables
from .models import User, Device, IPRange, DHCPConfig, SyslogMessage, Settings  # noqa: F401

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Web application for managing ISC DHCP server",
    docs_url="/api/docs" if settings.DEBUG else None,  # Disable docs in production
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Configure CORS (if enabled)
if settings.ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print(f"✓ CORS enabled: {settings.CORS_ORIGINS}")
else:
    print("⚠ CORS disabled")

# Setup security middleware (rate limiting, security headers)
# Can be disabled for deployments behind authenticated proxy
if settings.ENABLE_RATE_LIMITING or settings.ENABLE_SECURITY_HEADERS:
    from .middleware.security import RateLimitMiddleware, SecurityHeadersMiddleware

    if settings.ENABLE_RATE_LIMITING:
        app.add_middleware(RateLimitMiddleware)
        print("✓ Rate limiting enabled")
    else:
        print("⚠ Rate limiting disabled")

    if settings.ENABLE_SECURITY_HEADERS:
        app.add_middleware(SecurityHeadersMiddleware)
        print("✓ Security headers enabled")
    else:
        print("⚠ Security headers disabled")
else:
    print("⚠ All security middleware disabled")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    from .database import SessionLocal
    from .services.auth_service import create_admin_user_if_not_exists
    from .services.settings_service import create_default_settings_if_not_exists
    from .services.log_monitor import start_log_monitor
    from .services.cleanup_scheduler import start_cleanup_scheduler

    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Initialize database with defaults
    db = SessionLocal()
    try:
        # Create admin user from environment variables
        admin_user = create_admin_user_if_not_exists(
            db,
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD
        )
        if admin_user:
            print(f"✓ Admin user '{admin_user.username}' ready")

        # Create default settings if they don't exist
        create_default_settings_if_not_exists(db)
    finally:
        db.close()

    # Start log file monitor for device last_seen updates
    start_log_monitor()

    # Start cleanup scheduler
    start_cleanup_scheduler()

    print(f"✓ {settings.APP_NAME} v{settings.APP_VERSION} started")
    print(f"✓ Database: {settings.DATABASE_URL}")
    print(f"✓ DHCP Config: {settings.DHCP_CONFIG_PATH}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print(f"✗ {settings.APP_NAME} shutting down")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


# Include API routers
from .api.v1 import api as api_v1
app.include_router(api_v1.router, prefix="/api/v1")
