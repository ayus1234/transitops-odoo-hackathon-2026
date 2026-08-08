"""
API Rate Limiting System using Slowapi and Redis/In-Memory Storage.
Protects endpoints against brute-force attacks, DDoS, and API abuse.
"""
import os
from fastapi import Request
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    SLOWAPI_AVAILABLE = True
except ImportError:
    Limiter = None
    _rate_limit_exceeded_handler = None
    get_remote_address = lambda r: "127.0.0.1"
    RateLimitExceeded = Exception
    SLOWAPI_AVAILABLE = False


def get_user_or_ip_identifier(request: Request) -> str:
    """Identify request by User ID if authenticated, or Client IP address."""
    user = getattr(request.state, "user", None)
    if user and getattr(user, "id", None):
        return f"user:{user.id}"
    return get_remote_address(request)


# Dummy Limiter class if slowapi is missing in static analyzer environment
class DummyLimiter:
    def limit(self, limit_value):
        def decorator(func):
            return func
        return decorator


# Redis or Memory Storage Configuration
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

if SLOWAPI_AVAILABLE and Limiter is not None:
    try:
        limiter = Limiter(
            key_func=get_user_or_ip_identifier,
            storage_uri=redis_url,
            default_limits=["120/minute"]
        )
    except Exception:
        # Fallback to in-memory limiter if Redis is unreachable in test/dev
        limiter = Limiter(
            key_func=get_user_or_ip_identifier,
            default_limits=["120/minute"]
        )
else:
    limiter = DummyLimiter()

# Pre-defined Limit Constants
RATE_LIMIT_AUTH = "10/minute"
RATE_LIMIT_DISPATCH = "60/minute"
RATE_LIMIT_POD = "60/minute"
RATE_LIMIT_STRICT = "5/minute"
