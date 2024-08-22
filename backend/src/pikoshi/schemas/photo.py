from datetime import datetime

from pydantic import BaseModel


class PhotoBase(BaseModel):
    album_id: int
    file_name: str
    date: datetime


class Photo(PhotoBase):
    id: int

    class Config:
        orm_mode = True
