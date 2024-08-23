from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str
    salt: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class UserInput(BaseModel):
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
