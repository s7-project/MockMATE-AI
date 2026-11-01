from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import TokenResponse, UserCreate, UserLogin, UserResponse
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


# -------------------------
# USER REGISTRATION
# -------------------------


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register_user(user_data: UserCreate, db: Annotated[Session, Depends(get_db)]):

    # Check existing email
    existing_user = (
        db.query(User).filter(func.lower(User.email) == user_data.email.lower()).first()
    )

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create new user
    new_user = User(
        full_name=user_data.full_name.strip(),
        email=user_data.email.lower(),
        hashed_password=hashed_password,
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()

        raise HTTPException(status_code=400, detail="Email already registered")

    return new_user


# -------------------------
# USER LOGIN
# -------------------------


@router.post("/login", response_model=TokenResponse)
def login_user(user_data: UserLogin, db: Annotated[Session, Depends(get_db)]):

    # Find user
    user = (
        db.query(User).filter(func.lower(User.email) == user_data.email.lower()).first()
    )

    # Check user and password
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}


# -------------------------
# CURRENT USER PROFILE
# -------------------------


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: Annotated[User, Depends(get_current_user)]):

    return current_user
