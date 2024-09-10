from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .network import Network
from .photo import Photo
from .user import User


class Album(Base):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(30), unique=False, index=True)
    album_name: Mapped[str] = mapped_column(String(254), nullable=True)
    is_private: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)

    user: Mapped["User"] = relationship("User", back_populates="albums")
    photos: Mapped["Photo"] = relationship("Photo", back_populates="album")
    networks: Mapped["Network"] = relationship("Network", back_populates="album")

    def __repr__(self):
        return f"<Album(title='{self.title}', album_name='{self.album_name}', is_private={self.is_private})>"
