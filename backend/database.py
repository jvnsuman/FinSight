"""
SQLAlchemy engine + session setup.
Every model inherits from 'Base'. Every request gets a DB session via 'get_db'.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from backend.config import settings

# The engine manages the actual connection to Postgres
engine = create_engine(settings.DATABASE_URL)

# Each instance manages of SessionLocal is a new database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#All ORM models will inherit from this
Base = declarative_base()

def get_db():
    """
    FastAPI dependency - yields a DB session per request,
    and always close it afterword, even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
