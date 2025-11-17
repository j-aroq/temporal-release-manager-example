"""
Rate limiting middleware to prevent abuse and DOS attacks.

Implements token bucket algorithm for rate limiting requests per IP address.
"""

import time
from typing import Dict, Tuple
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter.

    Tracks request rates per IP address and enforces configurable limits.
    """

    def __init__(self, requests_per_minute: int = 60, burst_size: int = 10):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Sustained rate limit
            burst_size: Maximum burst of requests allowed
        """
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.refill_rate = requests_per_minute / 60.0  # tokens per second

        # Store (tokens, last_update_time) for each IP
        self.buckets: Dict[str, Tuple[float, float]] = defaultdict(
            lambda: (float(burst_size), time.time())
        )

    def is_allowed(self, client_ip: str) -> Tuple[bool, Dict[str, str]]:
        """
        Check if request from client IP is allowed.

        Args:
            client_ip: Client IP address

        Returns:
            Tuple of (is_allowed, headers_dict)
        """
        current_time = time.time()
        tokens, last_update = self.buckets[client_ip]

        # Refill tokens based on time elapsed
        time_elapsed = current_time - last_update
        tokens = min(
            self.burst_size,
            tokens + (time_elapsed * self.refill_rate)
        )

        # Check if we have enough tokens
        if tokens >= 1.0:
            # Consume one token
            tokens -= 1.0
            self.buckets[client_ip] = (tokens, current_time)

            headers = {
                "X-RateLimit-Limit": str(self.requests_per_minute),
                "X-RateLimit-Remaining": str(int(tokens)),
                "X-RateLimit-Reset": str(int(current_time + (1.0 / self.refill_rate))),
            }

            return True, headers
        else:
            # Rate limit exceeded
            retry_after = int((1.0 - tokens) / self.refill_rate)
            self.buckets[client_ip] = (tokens, current_time)

            headers = {
                "X-RateLimit-Limit": str(self.requests_per_minute),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(current_time + retry_after)),
                "Retry-After": str(retry_after),
            }

            return False, headers

    def cleanup_old_entries(self, max_age_seconds: int = 3600):
        """
        Remove old entries to prevent memory growth.

        Args:
            max_age_seconds: Maximum age of entries to keep
        """
        current_time = time.time()
        cutoff_time = current_time - max_age_seconds

        # Remove entries older than cutoff
        keys_to_remove = [
            ip for ip, (_, last_update) in self.buckets.items()
            if last_update < cutoff_time
        ]

        for ip in keys_to_remove:
            del self.buckets[ip]

        if keys_to_remove:
            logger.info(f"Cleaned up {len(keys_to_remove)} old rate limit entries")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting HTTP requests.

    Applies different rate limits to different endpoint categories.
    """

    def __init__(self, app, requests_per_minute: int = 60, burst_size: int = 10):
        """
        Initialize rate limit middleware.

        Args:
            app: FastAPI application
            requests_per_minute: Default rate limit
            burst_size: Maximum burst size
        """
        super().__init__(app)
        self.limiter = RateLimiter(requests_per_minute, burst_size)

        # More restrictive limits for auth endpoints
        self.auth_limiter = RateLimiter(requests_per_minute=10, burst_size=3)

        # Cleanup counter
        self.request_count = 0

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request with rate limiting.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response with rate limit headers

        Raises:
            HTTPException: If rate limit exceeded
        """
        # Skip rate limiting for health check endpoints
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get client IP (handle proxies)
        client_ip = self._get_client_ip(request)

        # Choose appropriate rate limiter
        if request.url.path.startswith("/api/auth"):
            limiter = self.auth_limiter
        else:
            limiter = self.limiter

        # Check rate limit
        is_allowed, headers = limiter.is_allowed(client_ip)

        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for IP {client_ip} on path {request.url.path}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers=headers,
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value

        # Periodic cleanup (every 1000 requests)
        self.request_count += 1
        if self.request_count % 1000 == 0:
            limiter.cleanup_old_entries()
            self.auth_limiter.cleanup_old_entries()

        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address, handling proxies.

        Args:
            request: Incoming request

        Returns:
            Client IP address
        """
        # Check X-Forwarded-For header (when behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP (client IP)
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fall back to direct client IP
        if request.client and request.client.host:
            return request.client.host

        return "unknown"
