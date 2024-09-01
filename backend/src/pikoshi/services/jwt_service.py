import os
from datetime import datetime, timedelta, timezone
from typing import Dict
from uuid import uuid4

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from pydantic import EmailStr
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..schemas.user import User
from ..services.security_service import SecurityService
from ..services.user_service import UserService

load_dotenv()

SECRET_KEY = str(os.environ.get("SECRET_KEY"))
ALGORITHM = str(os.environ.get("ALGORITHM"))


class JWTAuthService:
    @staticmethod
    def get_user_tokens(user_uuid: str) -> Dict[str, str]:
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

    @staticmethod
    def verify_token(token: str) -> None:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    @staticmethod
    async def signup_user_with_email(
        user_info,
        user_email: EmailStr,
        db: Session = Depends(get_db),
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
        new_user = UserService.create_user(db, new_user)

        if not new_user:
            raise HTTPException(
                status_code=409, detail="Email has already been registered."
            )

        user_from_db = UserService.get_user_by_email(db, user_email)
        UserService.set_user_as_active(db, user_from_db)
        UserService.update_user_last_login(db, user_from_db)
        return new_user

    @staticmethod
    async def authenticate_user_with_jwt(
        user_info, db: Session = Depends(get_db)
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

        user_from_db = UserService.get_user_by_email(db, user_email)
        if not user_from_db:
            raise HTTPException(status_code=400, detail="No User By That Email Found")

        user_password_from_db = user_from_db.password
        user_salt = user_from_db.salt
        user_is_verified = SecurityService.verify_value(
            user_password, user_password_from_db, user_salt  # type:ignore
        )

        if not user_is_verified:
            raise HTTPException(status_code=401, detail="Hashes in DB do not match")

        user_from_db = UserService.get_user_by_email(db, user_email)
        UserService.set_user_as_active(db, user_from_db)
        UserService.update_user_last_login(db, user_from_db)
        return user_from_db
