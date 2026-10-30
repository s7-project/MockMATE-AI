
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# SQLite database
DATABASE_URL = "sqlite:///./mock_interview.db"

# Database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class
class Base(DeclarativeBase):
    pass


# Database dependency
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
