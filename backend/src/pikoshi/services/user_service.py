from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from ..models.user import User
from ..schemas.user import UserCreate
from ..services.security_service import generate_salt, hash_value


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


# TODO: Add services (not in this file) related to generating first album, photo, and network
def generate_user_profile(user_name, user_password, user_email, salt) -> UserCreate:
    new_user = UserCreate(
        name=user_name, email=user_email, password=user_password, salt=salt
    )
    return new_user


def create_user(db: Session, user: UserCreate) -> User | None:
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        return None
    db_user = User(
        created=func.now(),
        name=user.name,
        email=user.email,
        password=user.password,
        salt=user.salt,
        is_active=True,
        last_login=func.now(),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def set_user_as_active(db: Session, user: User) -> None:
    user.__setattr__("is_active", True)
    db.add(user)
    db.commit()
