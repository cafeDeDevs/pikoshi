from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True)
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    file_name = Column(String(254), nullable=False)

    album = relationship("Album", back_populates="photos")

    def __repr__(self):
        return f"<Photo(file_name='{self.file_name}')>"
