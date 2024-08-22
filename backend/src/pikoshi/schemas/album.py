from pydantic import BaseModel


class AlbumBase(BaseModel):
    title: str
    album_name: str | None = None


class Album(AlbumBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
