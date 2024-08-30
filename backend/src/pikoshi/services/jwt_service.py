import os
from datetime import datetime, timedelta, timezone
from typing import Dict

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from pydantic import EmailStr
from sqlalchemy.orm import Session

from ..config.redis_config import redis_instance as redis
from ..dependencies import get_db
from ..services.security_service import generate_salt, hash_value, verify_value
from ..services.user_service import (
    create_user,
    generate_user_profile,
    get_user_by_email,
    set_user_as_active,
)

load_dotenv()

SECRET_KEY = str(os.environ.get("SECRET_KEY"))
ALGORITHM = str(os.environ.get("ALGORITHM"))


class JWTAuthService:
    @staticmethod
    def get_user_tokens() -> Dict[str, str]:
        # NOTE: Change each values to test invalidation of token logic
        access_token_expires = datetime.now(timezone.utc) + timedelta(
            hours=1
        )  # default
        refresh_token_expires = datetime.now(timezone.utc) + timedelta(
            hours=24
        )  # default

        access_token = jwt.encode(
            {
                "exp": access_token_expires,
                "iat": datetime.now(timezone.utc),
                "sub": "pikoshi jwt access token",
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        refresh_token = jwt.encode(
            {
                "exp": refresh_token_expires,
                "iat": datetime.now(timezone.utc),
                "sub": "pikoshi jwt refresh token",
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

        return {"access_token": access_token, "refresh_token": refresh_token}

    @staticmethod
    def verify_token(token: str) -> None:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    @staticmethod
    async def signup_user_with_email(
        user_info,
        user_email: EmailStr,
        access_token: str,
        db: Session = Depends(get_db),
    ) -> None:
        salt = generate_salt()
        user_name = user_info.username
        user_password = hash_value(user_info.password, salt)
        new_user = generate_user_profile(user_name, user_password, user_email, salt)
        new_user = create_user(db, new_user)

        if not new_user:
            raise HTTPException(
                status_code=409, detail="Email has already been registered."
            )

        user_from_db = get_user_by_email(db, user_email)
        user_id = user_from_db.id
        await redis.set(
            f"auth_session_{access_token}", user_id, ex=3600  # type:ignore
        )
        set_user_as_active(db, user_from_db)

    @staticmethod
    async def authenticate_user_with_jwt(
        user_info, access_token: str, db: Session = Depends(get_db)
    ) -> None:
        user_email = user_info.email
        user_password = user_info.password

        user_from_db = get_user_by_email(db, user_email)
        if not user_from_db:
            raise HTTPException(status_code=400, detail="No User By That Email Found")

        user_password_from_db = user_from_db.password
        user_salt = user_from_db.salt
        user_is_verified = verify_value(
            user_password, user_password_from_db, user_salt  # type:ignore
        )

        if not user_is_verified:
            raise HTTPException(status_code=401, detail="Hashes in DB do not match")

        user_from_db = get_user_by_email(db, user_email)
        user_id = user_from_db.id
        await redis.set(
            f"auth_session_{access_token}", user_id, ex=3600  # type:ignore
        )
        set_user_as_active(db, user_from_db)
