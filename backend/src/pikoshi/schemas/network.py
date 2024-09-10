from pydantic import BaseModel, ConfigDict


class NetworkBase(BaseModel):
    founder_id: int
    user_id: int
    album_id: int


class NetworkCreate(NetworkBase):
    pass


class Network(NetworkBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
