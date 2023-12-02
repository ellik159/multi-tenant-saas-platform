from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from src.database.session import SessionLocal, set_tenant_context
from src.core.security import decode_token
from jose import JWTError


class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to set tenant context for RLS
    Extracts organization_id from JWT and sets it in the database session
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip for public endpoints
        public_paths = ["/", "/health", "/docs", "/redoc", "/openapi.json", "/api/v1/auth/register", "/api/v1/auth/login"]
        
        if request.url.path in public_paths or request.url.path.startswith("/api/v1/subscriptions/webhook"):
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            
            try:
                payload = decode_token(token)
                organization_id = payload.get("organization_id")
                
                if organization_id:
                    # Store in request state for use in endpoints
                    request.state.organization_id = organization_id
                    request.state.user_id = payload.get("sub")
                    
                    # Set tenant context in database session
                    # This happens per-request in the dependency, not here
                    # We just store it in request state
                    
            except JWTError:
                pass  # Will be handled by endpoint authentication
        
        response = await call_next(request)
        return response
