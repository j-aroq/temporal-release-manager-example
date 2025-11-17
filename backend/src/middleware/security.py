"""
Security headers middleware for enhanced application security.

Adds various security headers to protect against common web vulnerabilities.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.

    Protects against:
    - XSS attacks
    - Clickjacking
    - MIME sniffing
    - Information leakage
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Add security headers to response.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response with security headers added
        """
        response = await call_next(request)

        # Prevent XSS attacks
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"

        # Content Security Policy (CSP)
        # Restrictive policy - adjust as needed for your app
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline'",  # unsafe-inline needed for some frameworks
            "style-src 'self' 'unsafe-inline'",   # unsafe-inline needed for Chakra UI
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Referrer Policy - control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (formerly Feature Policy)
        # Disable potentially dangerous features
        permissions_directives = [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()",
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions_directives)

        # HSTS (HTTP Strict Transport Security)
        # Force HTTPS for 1 year, including subdomains
        # Note: Only enable this when serving over HTTPS
        # response.headers["Strict-Transport-Security"] = (
        #     "max-age=31536000; includeSubDomains; preload"
        # )

        # Remove server identification headers
        if "Server" in response.headers:
            del response.headers["Server"]
        response.headers["X-Powered-By"] = ""  # Hide framework info

        return response
