"""
Database session management.

Provides SQLAlchemy engine and session factory for the gateway.
"""

from __future__ import annotations

import os
from typing import Generator, AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Database URL from environment, with sensible defaults for development
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    os.getenv("GATEWAY_DATABASE_URL", "sqlite:///./dev.db")
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=bool(os.getenv("SQL_ECHO", "").lower() == "true"),
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[Session, None]:
    """
    Database session dependency for FastAPI.
    
    Usage:
        @router.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
