from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..database import Base
from .album import Album


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    album_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("albums.id"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(254), nullable=False)

    album: Mapped["Album"] = relationship("Album", back_populates="photos")

    def __repr__(self):
        return f"<Photo(file_name='{self.file_name}')>"
