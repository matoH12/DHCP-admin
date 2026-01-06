"""
Security middleware for FastAPI application
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple
import time


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent brute force and DoS attacks

    Limits:
    - 100 requests per minute per IP for general endpoints
    - 5 login attempts per minute per IP
    - 1000 requests per hour per IP
    """

    def __init__(self, app):
        super().__init__(app)
        self.requests: Dict[str, list] = defaultdict(list)
        self.login_attempts: Dict[str, list] = defaultdict(list)

    def _clean_old_requests(self, ip: str, timeframe: timedelta):
        """Remove requests older than timeframe"""
        now = datetime.now()
        cutoff = now - timeframe
        self.requests[ip] = [ts for ts in self.requests[ip] if ts > cutoff]

    def _clean_old_login_attempts(self, ip: str, timeframe: timedelta):
        """Remove login attempts older than timeframe"""
        now = datetime.now()
        cutoff = now - timeframe
        self.login_attempts[ip] = [ts for ts in self.login_attempts[ip] if ts > cutoff]

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        now = datetime.now()

        # Rate limit for login endpoint (stricter)
        if request.url.path == "/api/v1/auth/login" and request.method == "POST":
            self._clean_old_login_attempts(client_ip, timedelta(minutes=1))

            if len(self.login_attempts[client_ip]) >= 5:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Too many login attempts. Please try again in 1 minute."
                    }
                )

            self.login_attempts[client_ip].append(now)

        # General rate limiting
        self._clean_old_requests(client_ip, timedelta(minutes=1))

        # Check requests per minute (100 req/min)
        if len(self.requests[client_ip]) >= 100:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Maximum 100 requests per minute."
                }
            )

        # Check requests per hour (1000 req/hour)
        hour_requests = [ts for ts in self.requests[client_ip] if ts > now - timedelta(hours=1)]
        if len(hour_requests) >= 1000:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Maximum 1000 requests per hour."
                }
            )

        self.requests[client_ip].append(now)

        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Remove server header (use del for MutableHeaders)
        if "Server" in response.headers:
            del response.headers["Server"]

        return response


def setup_security_middleware(app):
    """
    Setup all security middleware
    """
    # Add rate limiting
    app.add_middleware(RateLimitMiddleware)

    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Add trusted host middleware (prevents host header injection)
    # In production, configure with actual allowed hosts
    # app.add_middleware(
    #     TrustedHostMiddleware,
    #     allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
    # )
