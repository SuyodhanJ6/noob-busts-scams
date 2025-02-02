"""
Database session management.
"""

from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from src.settings import settings

# Create async engine
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Create sync engine for non-async operations
sync_engine = create_engine(
    settings.DATABASE_URL.replace("+aiomysql", "+pymysql"),
    echo=settings.DEBUG,
    future=True
)

# Create session factories
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

SessionLocal = sessionmaker(
    sync_engine,
    expire_on_commit=False
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session.
    
    Yields:
        AsyncSession instance
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_db() -> Generator[Session, None, None]:
    """
    Get synchronous database session.
    
    Yields:
        Session instance
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Aliases for backward compatibility
get_session = get_async_session 