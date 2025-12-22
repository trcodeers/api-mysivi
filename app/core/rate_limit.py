from slowapi import Limiter
from fastapi import Request
from slowapi.util import get_remote_address
from app.core.auth import get_current_user_optional

def rate_limit_key(request: Request) -> str:
    """
    Priority:
    1. Authenticated user (from access_token cookie)
    2. Client IP address
    """
    user = get_current_user_optional(request)

    if user:
        # assuming payload contains user_id or sub
        user_id = user.get("sub") or user.get("user_id")
        if user_id:
            return f"user:{user_id}"

    # fallback to IP-based throttling
    return get_remote_address(request)


limiter = Limiter(key_func=rate_limit_key)
