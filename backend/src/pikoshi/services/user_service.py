from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from ..models.item import Item
from ..models.user import User
from ..schemas.item import ItemCreate
from ..schemas.user import UserCreate
from ..services.security_service import generate_salt, hash_value, verify_value


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


# TODO: Add services (not in this file) related to generating first album, photo, and network
def generate_user_profile(user_info, user_password, salt) -> UserCreate:
    user_name = user_info.get("name")
    user_email = user_info.get("email")
    user_id = user_info.get("id")
    salt = generate_salt()
    user_password = hash_value(user_id, salt)
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


def create_user_item(db: Session, item: ItemCreate, user_id: int):
    db_item = Item(title=item.title, description=item.description, owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
