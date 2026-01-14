from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Local SQLite file DB (no setup)
SQLITE_URL = "sqlite:///./iot.db"

# SQLAlchemy 2.0 style engine (sync for simplicity)
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},  # needed for SQLite with threads
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_session() -> Session:
    """FastAPI dependency to get a DB session per request."""
    with SessionLocal() as session:
        yield session
