import time
from functools import wraps
from typing import Callable

import redis
from fastapi import HTTPException, Request
from src.settings import settings

# Initialize Redis client
redis_client = redis.from_url(settings.REDIS_URL)

def rate_limit(
    max_requests: int = 100,
    window_seconds: int = 3600
) -> Callable:
    """Rate limiting decorator"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Get client IP
            client_ip = request.client.host
            key = f"rate_limit:{client_ip}"
            
            # Check current request count
            current = redis_client.get(key)
            if current is not None and int(current) >= max_requests:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded"
                )
                
            # Increment request count
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            pipe.execute()
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator 