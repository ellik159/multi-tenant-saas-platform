from typing import Generator
from fastapi import Depends
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from src.core.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI routes
    Sets tenant context for RLS
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def set_tenant_context(db: Session, organization_id: str):
    """
    Set the current organization ID for RLS
    This is called by the TenantContextMiddleware
    """
    # Set session variable for PostgreSQL RLS using parameterized query to prevent SQL injection
    db.execute(text("SET app.current_organization_id = :org_id"), {"org_id": organization_id})
    db.commit()
