from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PhotoBase(BaseModel):
    album_id: int
    file_name: str
    date: datetime


class Photo(PhotoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
