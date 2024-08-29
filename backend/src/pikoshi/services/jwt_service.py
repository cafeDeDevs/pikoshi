import os
from datetime import datetime, timedelta, timezone
from typing import Dict

import jwt
from dotenv import load_dotenv

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
