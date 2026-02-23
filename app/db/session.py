import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

def _db_url() -> str:
    if settings.DATABASE_URL:
        return settings.DATABASE_URL
    # local fallback
    return "sqlite:///./data/local.db"

engine = create_engine(_db_url(), pool_pre_ping=True, future=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

class Base(DeclarativeBase):
    pass
