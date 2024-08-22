from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ..database import Base


class Network(Base):
    __tablename__ = "networks"

    id = Column(Integer, primary_key=True)
    founder_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=False)

    founder = relationship(
        "User", foreign_keys=[founder_id], back_populates="founded_networks"
    )
    user = relationship("User", foreign_keys=[user_id], back_populates="networks")
    album = relationship("Album", back_populates="networks")

    def __repr__(self):
        return f"<Networks(founder_id='{self.founder_id}', user_id='{self.user_id}')>"
