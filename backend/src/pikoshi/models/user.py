from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String(30), unique=False, index=True)
    password = Column(String(254), nullable=True)
    email = Column(Text, unique=True, index=True)
    is_active = Column(Boolean, nullable=True, default=True)
    last_login = Column(DateTime(timezone=True), onupdate=func.now())

    items = relationship("Item", back_populates="owner")

    def __repr__(self):
        return f"<User(name='{self.name}', email='{self.email}', is_active={self.is_active})>"
