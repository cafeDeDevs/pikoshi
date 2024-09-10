# TODO: Refactor these, too repetitive
# NOTE: Will require some thinking on the route handlers
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str
    salt: str
    uuid: str


class User(UserCreate):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserInput(BaseModel):
    email: EmailStr


class UserInputEmailPass(BaseModel):
    email: EmailStr

    password: Annotated[
        str,
        Field(
            min_length=10,
        ),
    ]

    @field_validator("password")
    def validate_password(cls, value):
        if not any(c.islower() for c in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")
        if not any(c in '!@#$%^&*()_+-=[]{};":\\|,.<>/?' for c in value):
            raise ValueError("Password must contain at least one special character")
        return value

    model_config = ConfigDict(from_attributes=True)


class UserInputPass(BaseModel):
    username: Annotated[str, Field(min_length=5)]
    password: Annotated[
        str,
        Field(
            min_length=10,
        ),
    ]
    token: str

    @field_validator("password")
    def validate_password(cls, value):
        if not any(c.islower() for c in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")
        if not any(c in '!@#$%^&*()_+-=[]{};":\\|,.<>/?' for c in value):
            raise ValueError("Password must contain at least one special character")
        return value

    model_config = ConfigDict(from_attributes=True)
