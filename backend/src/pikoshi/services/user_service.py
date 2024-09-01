from typing import List
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from ..models.user import User as UserModel
from ..schemas.user import User, UserCreate


class UserService:
    @staticmethod
    def get_user(db: Session, user_id: int) -> User:
        return db.query(UserModel).filter(UserModel.id == user_id).first()

    @staticmethod
    def get_user_by_uuid(db: Session, user_uuid: str) -> User:
        return db.query(UserModel).filter(UserModel.uuid == user_uuid).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        return db.query(UserModel).filter(UserModel.email == email).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    # TODO: Add services (not in this file) related to generating first album, photo, and network
    @staticmethod
    def generate_user_profile(
        user_name, user_password, user_email, salt, uuid
    ) -> UserCreate:
        new_user = UserCreate(
            name=user_name,
            email=user_email,
            password=user_password,
            salt=salt,
            uuid=uuid,
        )
        return new_user

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User | None:
        db_user = UserService.get_user_by_email(db, email=user.email)
        uuid = str(uuid4())
        if db_user:
            return None
        db_user = UserModel(
            created=func.now(),
            name=user.name,
            email=user.email,
            uuid=uuid,
            password=user.password,
            salt=user.salt,
            is_active=True,
            last_login=func.now(),
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def set_user_as_active(db: Session, user: User) -> None:
        user.__setattr__("is_active", True)
        db.add(user)
        db.commit()

    @staticmethod
    def update_user_last_login(db: Session, user: User) -> None:
        user.__setattr__("last_login", func.now())
        db.add(user)
        db.commit()

    @staticmethod
    def set_user_as_inactive(db: Session, user: User) -> None:
        user.__setattr__("is_active", False)
        db.add(user)
        db.commit()
