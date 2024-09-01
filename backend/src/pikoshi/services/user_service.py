from typing import List
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from ..models.user import User as UserModel
from ..schemas.user import User, UserCreate


class UserService:
    @staticmethod
    def get_user(db: Session, user_id: int) -> User:
        """
        - Grabs the user by PK id.
        """
        return db.query(UserModel).filter(UserModel.id == user_id).first()

    @staticmethod
    def get_user_by_uuid(db: Session, user_uuid: str) -> User:
        """
        - Grabs the user by UUID.
        """
        return db.query(UserModel).filter(UserModel.uuid == user_uuid).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        """
        - Grabs the User by Email.
        """
        return db.query(UserModel).filter(UserModel.email == email).first()

    # TODO: Add services (not in this file) related to generating first album, photo, and network
    @staticmethod
    def generate_user_profile(
        user_name, user_password, user_email, salt, uuid
    ) -> UserCreate:
        """
        - Generates a User Profile to later be inserted into DB
        """
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
        """
        - Grabs the User By Email.
        - Establishes a new random UUID.
        - Prepares SQLAlchemy Statement and assigns it the `db_user`.
        - Adds and Commits new User data to user table DB.
        - Refresh DB via to ensure DB does not retain in memory data.
        - Return the new User from the DB.
        """
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
        """
        - Sets the User's `is_active` field to True.
        """
        user.__setattr__("is_active", True)
        db.add(user)
        db.commit()
        db.refresh(user)

    @staticmethod
    def update_user_last_login(db: Session, user: User) -> None:
        """
        - Updates user's last_login to current time.
        """
        user.__setattr__("last_login", func.now())
        db.add(user)
        db.commit()
        db.refresh(user)

    @staticmethod
    def set_user_as_inactive(db: Session, user: User) -> None:
        """
        - Sets the User's `is_active` field to False.
        """
        user.__setattr__("is_active", False)
        db.add(user)
        db.commit()
        db.refresh(user)
