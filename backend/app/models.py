from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Full name
    full_name = Column(String(100), nullable=False)

    # Email
    email = Column(String(150), unique=True, index=True, nullable=False)

    # Hashed password
    hashed_password = Column(String(255), nullable=False)

    # Account creation date
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
