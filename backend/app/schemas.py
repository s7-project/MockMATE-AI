
from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
    Field
)


# Registration schema
class UserCreate(BaseModel):

    full_name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )


# Login schema
class UserLogin(BaseModel):

    email: EmailStr

    password: str


# User response schema
class UserResponse(BaseModel):

    id: int

    full_name: str

    email: EmailStr

    model_config = ConfigDict(
        from_attributes=True
    )


# JWT token response schema
class TokenResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"
