from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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
            pattern=r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=[\]{};":\\|,.<>/?])',
        ),
    ]
