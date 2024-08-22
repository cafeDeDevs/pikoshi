from pydantic import BaseModel, ConfigDict

from .item import Item


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    model_config = ConfigDict(from_attributes=True)
