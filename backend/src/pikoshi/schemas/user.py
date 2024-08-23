from pydantic import BaseModel, ConfigDict

from .item import Item


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
    items: list[Item] = []

    class Config:
        from_attributes = True
