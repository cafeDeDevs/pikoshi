from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ..database import Base


# TODO: Consider putting certain fields in a separate table
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    name: Mapped[str] = mapped_column(String(30), unique=False, index=True)
    password: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    salt: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(Text, unique=True, index=True)
    uuid: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    last_login: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    signed_up_method: Mapped[str] = mapped_column(
        String, nullable=False, default="email"
    )

    def __repr__(self):
        return f"<User(name='{self.name}', email='{self.email}', is_active={self.is_active})>"
