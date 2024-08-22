from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from ..models.item import Item
from ..models.user import User
from ..schemas.item import ItemCreate
from ..schemas.user import UserCreate


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = User(
        created=func.now(),
        name=user.name,
        email=user.email,
        password=fake_hashed_password,
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
