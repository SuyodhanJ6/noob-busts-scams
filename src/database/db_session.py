from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.settings import settings
from src.utils.database import Base

# Create engine
engine = create_engine(settings.DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Database session context manager"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 