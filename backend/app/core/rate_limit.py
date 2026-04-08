from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
import time

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

# Rate limit exceeded handler
def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return {
        "error": "Rate limit exceeded",
        "message": f"Too many requests. Try again in {exc.retry_after} seconds.",
        "retry_after": exc.retry_after
    }

# Rate limit configurations
RATE_LIMITS = {
    "auth": "5/minute",  # 5 requests per minute for auth endpoints
    "orders": "10/minute",  # 10 orders per minute
    "general": "100/minute",  # 100 requests per minute for general endpoints
    "admin": "200/minute",  # 200 requests per minute for admin endpoints
}
