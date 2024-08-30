import os
from typing import Dict

import httpx
from dotenv import load_dotenv
from fastapi import Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from ..config.redis_config import redis_instance as redis
from ..dependencies import get_db
from ..schemas.user import User
from ..services.security_service import generate_salt, hash_value, verify_value
from ..services.user_service import (
    create_user,
    generate_user_profile,
    get_user_by_email,
    set_user_as_active,
)

load_dotenv()


class GoogleOAuthService:
    @staticmethod
    async def get_user_tokens(auth_code) -> Dict[str, str]:
        data = {
            "code": auth_code,
            "client_id": os.environ.get("GOOGLE_OAUTH2_CLIENT_ID"),
            "client_secret": os.environ.get("GOOGLE_OAUTH2_CLIENT_SECRET"),
            "redirect_uri": os.environ.get("GOOGLE_OAUTH2_REDIRECT_URI"),
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.googleapis.com/oauth2/v4/token", data=data
            )
        if response.status_code != 200:
            raise ValueError(
                "Error Occurred While Getting Tokens Via Google Auth Code."
            )
        return response.json()

    @staticmethod
    async def get_user_info(access_token: str) -> Dict[str, str]:
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(user_info_url, headers=headers)
        if response.status_code != 200:
            raise ValueError(
                "An Error Occurred While Authenticating User By Access Token."
            )
        return response.json()

    @staticmethod
    async def get_user_from_db(
        access_token: str, db: Session = Depends(get_db)
    ) -> User:
        user_info = await GoogleOAuthService.get_user_info(access_token)
        user_email = user_info.get("email")
        if not user_email:
            raise ValueError("No User Email Found by Access Token")
        user = get_user_by_email(db, user_email)

        if not user:
            raise ValueError("User not found in DB")
        return user

    @staticmethod
    # TODO: User schema needs to be adjusted to return User type in this case...
    def get_user_by_email_from_db(user_info, db: Session = Depends(get_db)):
        user_email = str(user_info.get("email"))
        user_from_db = get_user_by_email(db, user_email)
        if not user_from_db:
            raise HTTPException(status_code=400, detail="No User By That Email Found")
        return user_from_db

    @staticmethod
    async def signup_user_with_google(
        user_info, access_token: str, db: Session = Depends(get_db)
    ) -> None:
        """
        - Creates a User instance in DB using fields grabbed from Google OAuth2 Services.
        - Generates Unique Salt and stores it in DB.
        - Utilizes the user_id instead of a user inputted password for
          password field since we don't have access to user's actual password
          using this sign up method (also hashes the user_id as if it were a password).
        - Creates a user session in redis, using the access_token as the key,
          and the new_user.id as the value. Lasts as long as the default access_token expiry.
        - Toggles the user's is_active field in the DB to True.
        """
        user_id = str(user_info.get("id"))
        salt = generate_salt()
        user_name = user_info.get("name")
        user_email = user_info.get("email")
        user_password = hash_value(user_id, salt)
        new_user = generate_user_profile(user_name, user_password, user_email, salt)
        new_user = create_user(db, new_user)
        if not new_user:
            raise HTTPException(
                status_code=409, detail="Email has already been registered."
            )
        await redis.set(
            f"auth_session_{access_token}", new_user.id, ex=3600  # type:ignore
        )
        set_user_as_active(db, new_user)

    @staticmethod
    async def authenticate_user_with_google(
        user_info, user_from_db, access_token: str, db: Session = Depends(get_db)
    ) -> None:
        """
        - Grabs the User's Google Id from Google OAuth2 Services.
        - Grabs the User's hashed/salted/peppered password from the DB.
        - Grabs the User's salt from the DB.
        - Verifies that the hashed/salted/peppered user_id matches the
          password retreived from the DB.
        - Grabs the User's Pikoshi DB id (different from Google ID).
        - Sets in the redis cache the session via the access_token as the key,
          and the user id from the DB as the value. Lasts as long as the default
          access_token expiry.
        - Toggles the user's is_active field in the DB to True.
        """
        user_id = str(user_info.get("id"))
        user_password = str(user_from_db.password)
        user_salt = str(user_from_db.salt)
        user_is_verified = verify_value(user_id, user_password, user_salt)
        if not user_is_verified:
            raise HTTPException(status_code=401, detail="Hashes in DB do not match")

        # TODO:
        # [x] Set user.is_active to true in DB,
        # [ ] update user.last_login to now
        user_id = user_from_db.id
        await redis.set(f"auth_session_{access_token}", user_id, ex=3600)  # type:ignore
        set_user_as_active(db, user_from_db)
