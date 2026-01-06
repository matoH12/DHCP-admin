"""
DHCP Admin - Main FastAPI application
"""
from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse
from .config import settings
from .database import engine, Base
from .middleware import setup_security_middleware
from .dependencies import get_current_user
from .models.user import User

# Import models to create tables
from .models import User, Device, IPRange, DHCPConfig, SyslogMessage, Settings  # noqa: F401

# Create FastAPI app with docs disabled (we'll create custom protected endpoints)
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Web application for managing ISC DHCP server",
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
    openapi_url=None,  # Disable default OpenAPI JSON
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
    from .services.syslog_server import start_syslog_server_thread

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

    # Start syslog UDP server for receiving DHCP server logs
    start_syslog_server_thread(host='0.0.0.0', port=514)

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


# Protected API Documentation Endpoints
@app.get("/api/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(current_user: User = Depends(get_current_user)):
    """
    OpenAPI JSON schema (protected by authentication)

    Requires: Valid JWT token in Authorization header
    """
    return JSONResponse(
        content=get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
    )


@app.get("/api/docs", include_in_schema=False, response_class=HTMLResponse)
async def get_swagger_documentation(request: Request, current_user: User = Depends(get_current_user)):
    """
    Swagger UI documentation (protected by authentication)

    Requires: Valid JWT token in Authorization header
    """
    # Get the token from the request
    auth_header = request.headers.get("authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""

    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{app.title} - Swagger UI</title>
        <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.10.5/swagger-ui.css" />
        <link rel="icon" type="image/png" href="/favicon.ico" />
        <style>
            html {{ box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }}
            *, *:before, *:after {{ box-sizing: inherit; }}
            body {{ margin:0; padding:0; }}
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.10.5/swagger-ui-bundle.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.10.5/swagger-ui-standalone-preset.js"></script>
        <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: "/api/openapi.json",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                requestInterceptor: (request) => {{
                    request.headers['Authorization'] = 'Bearer {token}';
                    return request;
                }},
                onComplete: () => {{
                    // Pre-authorize with the token
                    ui.preauthorizeApiKey("HTTPBearer", "Bearer {token}");
                }}
            }});
            window.ui = ui;
        }};
        </script>
    </body>
    </html>
    """)


@app.get("/api/redoc", include_in_schema=False, response_class=HTMLResponse)
async def get_redoc_documentation(request: Request, current_user: User = Depends(get_current_user)):
    """
    ReDoc documentation (protected by authentication)

    Requires: Valid JWT token in Authorization header
    """
    # Get the token from the request
    auth_header = request.headers.get("authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""

    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{app.title} - ReDoc</title>
        <link rel="icon" type="image/png" href="/favicon.ico" />
        <style>
            body {{ margin: 0; padding: 0; }}
        </style>
    </head>
    <body>
        <redoc spec-url="/api/openapi.json"></redoc>
        <script src="https://cdn.jsdelivr.net/npm/redoc@2.1.3/bundles/redoc.standalone.js"></script>
        <script>
        // Add authorization header to all requests
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {{}}) {{
            if (!options.headers) {{
                options.headers = {{}};
            }}
            options.headers['Authorization'] = 'Bearer {token}';
            return originalFetch(url, options);
        }};
        </script>
    </body>
    </html>
    """)


# Include API routers
from .api.v1 import api as api_v1
app.include_router(api_v1.router, prefix="/api/v1")
