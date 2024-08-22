from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(30), unique=False, index=True)
    album_name = Column(String(254), nullable=True)
    is_private = Column(Boolean, nullable=True, default=True)

    user = relationship("User", back_populates="albums")
    photos = relationship("Photo", back_populates="album")
    networks = relationship("Network", back_populates="album")

    def __repr__(self):
        return f"<Album(title='{self.title}', album_name='{self.album_name}', is_private={self.is_private})>"
