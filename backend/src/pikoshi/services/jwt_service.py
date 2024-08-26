import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = str(os.environ.get("SECRET_KEY"))
ALGORITHM = str(os.environ.get("ALGORITHM"))


class JWTAuthService:
    @staticmethod
    #  def get_user_tokens(encrypted_email_str):
    def get_user_tokens():
        # NOTE: Change each values to test invalidation of token logic
        #  access_token_expires = datetime.now(timezone.utc) + timedelta(hours=1) # default
        access_token_expires = datetime.now(timezone.utc) + timedelta(minutes=1)
        refresh_token_expires = datetime.now(timezone.utc) + timedelta(
            hours=24
        )  # default

        access_token = jwt.encode(
            {
                "exp": access_token_expires,
                "iat": datetime.now(timezone.utc),
                # TODO: Put encrypted email string here OR UUID, think on it...
                # so that we can set is_active flag in DB to true/false
                # and also against redis cache on reaffirming authentication (i.e. check_auth_context route)
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

    @staticmethod
    def is_jwt(token):
        """Check if a token is a JWT based on its structure."""
        return token.count(".") == 2
