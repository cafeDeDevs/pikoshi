import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = str(os.environ.get("SECRET_KEY"))
ALGORITHM = str(os.environ.get("ALGORITHM"))


class JWTAuthService:
    @staticmethod
    def get_user_tokens():
        access_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        refresh_token_expires = datetime.now(timezone.utc) + timedelta(hours=24)

        access_token = jwt.encode(
            {
                "exp": access_token_expires,
                "iat": datetime.now(timezone.utc),
                "sub": "pikoshi access token",
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        refresh_token = jwt.encode(
            {
                "exp": refresh_token_expires,
                "iat": datetime.now(timezone.utc),
                "sub": "pikoshi refresh token",
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

        return {"access_token": access_token, "refresh_token": refresh_token}
