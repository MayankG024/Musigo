"""Rate limiting configuration and middleware"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request
from api.core.config import settings


def get_client_identifier(request: Request) -> str:
    """
    Get client identifier for rate limiting.
    Uses IP address as primary identifier since we don't have user auth.
    In production, consider using X-Forwarded-For if behind a proxy.
    """
    # Check for proxy headers first
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For can contain multiple IPs, take the first one
        return forwarded.split(",")[0].strip()
    
    # Fall back to direct client IP
    return get_remote_address(request)


# Initialize limiter with configurable storage
# Use Redis for distributed rate limiting across multiple instances
# Falls back to in-memory for single-instance deployments
limiter = Limiter(
    key_func=get_client_identifier,
    default_limits=["200/minute"],  # Global default: 200 requests per minute per IP
    storage_uri=settings.RATE_LIMIT_STORAGE,
    strategy="fixed-window",  # Options: fixed-window, moving-window
    headers_enabled=True,  # Add rate limit info to response headers
    enabled=settings.RATE_LIMIT_ENABLED,
)


def setup_rate_limiting(app):
    """Setup rate limiting for the FastAPI app"""
    # Add rate limit exceeded handler
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Add SlowAPI middleware
    app.add_middleware(SlowAPIMiddleware)


# Pre-configured rate limit decorators for different endpoint types

# Strict limits for write operations (POST, PUT, DELETE)
strict_limit = limiter.limit("30/minute")

# Moderate limits for read operations
moderate_limit = limiter.limit("100/minute")

# Lenient limits for static/public endpoints
lenient_limit = limiter.limit("200/minute")

# Very strict for expensive operations (AI, embeddings, etc)
expensive_limit = limiter.limit("10/minute")

# Auth endpoints (even though we're using demo mode, keep for future)
auth_limit = limiter.limit("5/minute")
