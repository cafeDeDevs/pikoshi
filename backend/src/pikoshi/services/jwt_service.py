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
    def is_jwt(token):
        """Check if a token is a JWT based on its structure."""
        return token.count(".") == 2

    @staticmethod
    def verify_token(token: str):
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
