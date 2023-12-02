from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import time
import json
from src.database.session import SessionLocal
from src.models.base import AuditLog
from src.core.config import settings


class AuditLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all API requests to audit_logs table
    """
    
    async def dispatch(self, request: Request, call_next):
        if not settings.ENABLE_AUDIT_LOGS:
            return await call_next(request)
        
        # Skip audit logging for health checks and docs
        skip_paths = ["/health", "/docs", "/redoc", "/openapi.json"]
        if request.url.path in skip_paths:
            return await call_next(request)
        
        start_time = time.time()
        
        # Get request details
        organization_id = getattr(request.state, "organization_id", None)
        user_id = getattr(request.state, "user_id", None)
        
        response = await call_next(request)
        
        # Only log if we have org context and it's not a GET request
        # (to avoid cluttering logs with read operations)
        if organization_id and request.method != "GET":
            process_time = time.time() - start_time
            
            # Determine action based on method and path
            action = self._determine_action(request.method, request.url.path)
            resource_type = self._extract_resource_type(request.url.path)
            
            details = {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": round(process_time, 3)
            }
            
            # Save to database in background to avoid blocking the request
            # Using queue-based approach with Celery would be better for production
            import asyncio
            asyncio.create_task(self._log_to_database(
                organization_id, user_id, action, resource_type,
                details, request.client.host if request.client else None,
                request.headers.get("user-agent")
            ))
        
        return response
    
    def _determine_action(self, method: str, path: str) -> str:
        """Determine action name from method and path"""
        if method == "POST":
            return "create"
        elif method == "PUT" or method == "PATCH":
            return "update"
        elif method == "DELETE":
            return "delete"
        else:
            return method.lower()
    
    def _extract_resource_type(self, path: str) -> str:
        """Extract resource type from path"""
        # Simple extraction: /api/v1/users -> users
        parts = path.split("/")
        if len(parts) >= 4:
            return parts[3]
        return "unknown"
    
    async def _log_to_database(self, organization_id, user_id, action, 
                                resource_type, details, ip_address, user_agent):
        """Background task to save audit log to database"""
        try:
            db = SessionLocal()
            audit_log = AuditLog(
                organization_id=organization_id,
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                details=json.dumps(details),
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.add(audit_log)
            db.commit()
            db.close()
        except Exception as e:
            # Don't fail request if audit logging fails
            print(f"Audit log error: {e}")
