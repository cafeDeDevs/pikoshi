from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .album import Album
from .user import User


class Network(Base):
    __tablename__ = "networks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    founder_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    album_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("albums.id"), nullable=False
    )

    founder: Mapped["User"] = relationship(
        "User", foreign_keys=[founder_id], back_populates="founded_networks"
    )
    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="networks"
    )
    album: Mapped["Album"] = relationship("Album", back_populates="networks")

    def __repr__(self):
        return f"<Networks(founder_id='{self.founder_id}', user_id='{self.user_id}')>"
