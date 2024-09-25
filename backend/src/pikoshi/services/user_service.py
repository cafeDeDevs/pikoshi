from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from ..models.user import User as UserModel
from ..schemas.user import User, UserCreate


async def get_user(db_session: AsyncSession, user_id: int) -> UserModel:
    """
    - Grabs the user by PK id.
    """
    stmt = select(UserModel).filter(UserModel.id == user_id)
    result = await db_session.execute(stmt)
    user = result.scalars().first()
    return user


async def get_user_by_uuid(db_session: AsyncSession, user_uuid: str) -> UserModel:
    """
    - Grabs the user by UUID.
    """
    stmt = select(UserModel).filter(UserModel.uuid == user_uuid)
    result = await db_session.execute(stmt)
    user = result.scalars().first()
    return user


async def get_user_by_email(db_session: AsyncSession, email: str) -> UserModel:
    """
    - Grabs the User by Email.
    """
    stmt = select(UserModel).filter(UserModel.email == email)
    result = await db_session.execute(stmt)
    user = result.scalars().first()
    return user


# TODO: Add services (not in this file) related to generating first album, photo, and network
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


async def create_user(db_session: AsyncSession, user: UserCreate, method: str = 'email') -> UserModel | None:
    """
    - Grabs the User By Email.
    - Establishes a new random UUID.
    - Prepares SQLAlchemy Statement and assigns it the `db_user`.
    - Adds and Commits new User data to user table DB.
    - Refresh DB via to ensure DB does not retain in memory data.
    - Return the new User from the DB.
    """
    db_user = await get_user_by_email(db_session, email=user.email)
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
        signed_up_method=method
    )
    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)
    return db_user


async def set_user_as_active(db_session: AsyncSession, user: User) -> None:
    """
    - Sets the User's `is_active` field to True.
    """
    user.__setattr__("is_active", True)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)


async def update_user_last_login(db_session: AsyncSession, user: User) -> None:
    """
    - Updates user's last_login to current time.
    """
    user.__setattr__("last_login", func.now())
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)


async def set_user_as_inactive(db_session: AsyncSession, user: User) -> None:
    """
    - Sets the User's `is_active` field to False.
    """
    user.__setattr__("is_active", False)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
