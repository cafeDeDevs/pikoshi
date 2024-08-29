import os
from typing import Dict

import httpx
from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..schemas.user import User
from ..services.user_service import get_user_by_email

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
