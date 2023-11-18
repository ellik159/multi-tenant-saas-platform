from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from src.core.config import settings
from src.middleware.tenant_context import TenantContextMiddleware
from src.middleware.rate_limiter import RateLimiterMiddleware
from src.middleware.audit_logger import AuditLoggerMiddleware
from src.api import auth, organizations, users, subscriptions, audit_logs
from src.database.session import engine
from src.models import base  # Import to register models

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware - order matters!
app.add_middleware(AuditLoggerMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(TenantContextMiddleware)


# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(organizations.router, prefix=f"{settings.API_V1_PREFIX}/organizations", tags=["Organizations"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["Users"])
app.include_router(subscriptions.router, prefix=f"{settings.API_V1_PREFIX}/subscriptions", tags=["Subscriptions"])
app.include_router(audit_logs.router, prefix=f"{settings.API_V1_PREFIX}/audit-logs", tags=["Audit Logs"])


@app.get("/")
async def root():
    return {
        "message": "Multi-Tenant SaaS Platform API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    # TODO: add more comprehensive checks
    from src.database.session import SessionLocal
    from src.core.redis_client import redis_client
    
    health_status = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": time.time()
    }
    
    # Check database
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        redis_client.ping()
        health_status["redis"] = "connected"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler - catches unhandled exceptions"""
    # TODO: add proper logging here
    print(f"Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "internal_error"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
