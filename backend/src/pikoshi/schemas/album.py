from pydantic import BaseModel, ConfigDict


class AlbumBase(BaseModel):
    title: str
    album_name: str | None = None


class Album(AlbumBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
