import os
from datetime import datetime, timedelta, timezone
from typing import Dict
from uuid import uuid4

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db_session
from ..schemas.user import User
from ..services import exception_handler_service as ExceptionService
from ..services import security_service as SecurityService
from ..services import user_service as UserService

load_dotenv()

SECRET_KEY = str(os.environ.get("SECRET_KEY"))
ALGORITHM = str(os.environ.get("ALGORITHM"))


def get_user_tokens(user_uuid: str) -> Dict[str, str]:
    """
    - Establishes respective expiry times for both JWT access_token and
      JWT refresh_token.
    - Encodes two new JWTs, one JWT access_token, one JWT refresh_token.
    - Encodes the User's UUID into the `sub` field of both JWTs.
    - Returns a dictionary with both JWT access_token and JWT refresh_token.
    """
    access_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)  # default
    refresh_token_expires = datetime.now(timezone.utc) + timedelta(hours=24)  # default

    access_token = jwt.encode(
        {
            "exp": access_token_expires,
            "iat": datetime.now(timezone.utc),
            "sub": user_uuid,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    refresh_token = jwt.encode(
        {
            "exp": refresh_token_expires,
            "iat": datetime.now(timezone.utc),
            "sub": user_uuid,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return {"access_token": access_token, "refresh_token": refresh_token}


def verify_token(token: str) -> Dict[str, str] | None:
    """
    - Decodes the JWT and returns all values inside if successful
      (i.e. JWT is not expired or corrupted).
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as e:
        ExceptionService.handle_generic_exception(e)
        return None


async def signup_user_with_email(
    user_info,
    user_email: EmailStr,
    db_session: AsyncSession = Depends(get_db_session),
    method="email",
) -> User:
    """
    - Creates a User instance in DB using fields grabbed from Front End Forms
    - Generates Unique Salt and stores it in DB.
    - Hashes,salts, and peppers the User's Inputted Password, and stores the
      hashed password and salt in the DB.
    - Toggles the user's is_active field in the DB to True.
    """
    salt = SecurityService.generate_salt()
    user_name = user_info.username
    user_password = SecurityService.hash_value(user_info.password, salt)
    uuid = str(uuid4())
    new_user = UserService.generate_user_profile(
        user_name, user_password, user_email, salt, uuid
    )
    new_user = await UserService.create_user(db_session, new_user, method)

    if not new_user:
        raise HTTPException(
            status_code=409, detail="Email has already been registered."
        )

    user_from_db = await UserService.get_user_by_email(db_session, user_email)
    await UserService.set_user_as_active(db_session, user_from_db)
    await UserService.update_user_last_login(db_session, user_from_db)
    return new_user


async def authenticate_user_with_jwt(
    user_info, db_session: AsyncSession = Depends(get_db_session)
) -> User:
    """
    - Grabs the User's Email and Password From Front End Forms.
    - Grabs the User's hashed/salted/peppered password from the DB.
    - Grabs the User's salt from the DB.
    - Verifies that the hashed/salted/peppered user_id matches the
      password retreived from the DB.
    - Grabs the User's Pikoshi DB id.
    - Toggles the user's is_active field in the DB to True.
    """
    user_email = user_info.email
    user_password = user_info.password

    user_from_db = await UserService.get_user_by_email(db_session, user_email)
    if not user_from_db:
        raise HTTPException(status_code=400, detail="No User By That Email Found")

    user_password_from_db = user_from_db.password
    user_salt = user_from_db.salt
    user_is_verified = SecurityService.verify_value(
        user_password, user_password_from_db, user_salt  # type:ignore
    )

    if not user_is_verified:
        raise HTTPException(status_code=401, detail="Hashes in DB do not match")

    user_from_db = await UserService.get_user_by_email(db_session, user_email)
    await UserService.set_user_as_active(db_session, user_from_db)
    await UserService.update_user_last_login(db_session, user_from_db)
    return user_from_db


def create_access_token(user_uuid: str) -> str:
    access_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
    access_token = jwt.encode(
        {
            "exp": access_token_expires,
            "iat": datetime.now(timezone.utc),
            "sub": user_uuid,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return access_token
