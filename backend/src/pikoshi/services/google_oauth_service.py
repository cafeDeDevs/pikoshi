import os

import httpx
from dotenv import load_dotenv

load_dotenv()


class GoogleOAuthService:
    @staticmethod
    def get_oauth_config(auth_code):
        return {
            "code": auth_code,
            "client_id": os.environ.get("GOOGLE_OAUTH2_CLIENT_ID"),
            "client_secret": os.environ.get("GOOGLE_OAUTH2_CLIENT_SECRET"),
            "redirect_uri": os.environ.get("GOOGLE_OAUTH2_REDIRECT_URI"),
            "grant_type": "authorization_code",
        }

    @staticmethod
    async def get_user_info(data):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.googleapis.com/oauth2/v4/token", data=data
            )
        if response.status_code == 200:
            return response.json()
        return None
