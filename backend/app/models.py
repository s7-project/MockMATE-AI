
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # User full name
    full_name = Column(
        String(100),
        nullable=False
    )

    # Email address (unique)
    email = Column(
        String(150),
        unique=True,
        index=True,
        nullable=False
    )

    # Securely hashed password
    hashed_password = Column(
        String(255),
        nullable=False
    )

    # Account creation timestamp
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
