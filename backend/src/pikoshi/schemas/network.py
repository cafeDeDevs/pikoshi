from pydantic import BaseModel


class NetworkBase(BaseModel):
    founder_id: int
    user_id: int
    album_id: int


class NetworkCreate(NetworkBase):
    pass


class Network(NetworkBase):
    id: int

    class Config:
        orm_mode = True
