from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
from src.core.redis_client import redis_client
from src.core.config import settings


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis
    Implements sliding window algorithm per organization
    """
    
    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # Skip rate limiting for public endpoints
        public_paths = ["/", "/health", "/docs", "/redoc", "/openapi.json"]
        if request.url.path in public_paths:
            return await call_next(request)
        
        # Get organization_id from request state (set by TenantContextMiddleware)
        organization_id = getattr(request.state, "organization_id", None)
        
        if not organization_id:
            # No org context, skip rate limiting (will fail auth anyway)
            return await call_next(request)
        
        # Get rate limit based on subscription tier
        # TODO: fetch actual tier from database
        # For now, assume free tier
        rate_limit = settings.RATE_LIMIT_FREE_TIER
        window = 3600  # 1 hour in seconds
        
        # Redis key for this organization
        key = f"rate_limit:{organization_id}"
        
        try:
            current_time = int(time.time())
            
            # Sliding window implementation
            pipe = redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, current_time - window)
            
            # Count requests in current window
            pipe.zcard(key)
            
            # Add current request
            user_id = getattr(request.state, "user_id", "anonymous")
            pipe.zadd(key, {f"{current_time}:{user_id}": current_time})
            
            # Set expiry
            pipe.expire(key, window)
            
            results = pipe.execute()
            request_count = results[1]
            
            # Check if rate limit exceeded
            if request_count >= rate_limit:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Rate limit exceeded",
                        "limit": rate_limit,
                        "window": "1 hour"
                    }
                )
            
            # Add rate limit headers to response
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(rate_limit)
            response.headers["X-RateLimit-Remaining"] = str(rate_limit - request_count - 1)
            response.headers["X-RateLimit-Reset"] = str(current_time + window)
            
            return response
            
        except Exception as e:
            # If Redis fails, allow request but log error
            print(f"Rate limiter error: {e}")
            return await call_next(request)
