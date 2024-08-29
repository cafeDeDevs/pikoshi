from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..config.redis_config import redis_instance as redis
from ..dependencies import get_db
from ..services.user_service import get_user
from .google_oauth_service import GoogleOAuthService
from .jwt_service import JWTAuthService

# TODO: Implement logic re: refreshing of access_token using refresh_token logic
# NOTE: See fastapi-with-google POC for refresh_access_token logic for google-oauth2.
# And also issue new access_token if refresh_token is still good (whether jwt or google-oauth2 token)


class AuthService:
    @staticmethod
    def is_jwt(token) -> bool:
        """Check if a token is a JWT based on its structure."""
        return token.count(".") == 2

    @staticmethod
    def is_google_oauth_token(token) -> bool:
        """Check if a token is a Google OAuth2 Token based on its structure."""
        return token.count(".") != 2

    @staticmethod
    async def authenticate_jwt(
        access_token: str,
        db: Session = Depends(get_db),
    ) -> JSONResponse:
        JWTAuthService.verify_token(access_token)
        user_id = int(await redis.get(f"auth_session_{access_token}"))
        user = get_user(db, user_id)
        if user and user.is_active:  # type:ignore
            return JSONResponse(
                status_code=200,
                content={"message": "User Is Authenticated With JWTs."},
            )
        else:
            raise HTTPException(
                status_code=401, detail="No User Found Within DB or User Not Active"
            )

    @staticmethod
    async def authenticate_google_oauth(
        access_token: str, db: Session = Depends(get_db)
    ) -> JSONResponse:
        user = await GoogleOAuthService.get_user_from_db(access_token, db)
        user_id_from_access_token = user.id
        user_id_from_redis = int(await redis.get(f"auth_session_{access_token}"))
        if user_id_from_access_token != user_id_from_redis:  # type:ignore
            raise HTTPException(
                status_code=401, detail="Token identifiers do not match."
            )

        if user and user.is_active == True:  # type:ignore
            return JSONResponse(
                status_code=200,
                content={"message": "User Is Authenticated With Google OAuth2."},
            )
        else:
            raise HTTPException(
                status_code=401, detail="No User Found Within DB or User Not Active"
            )
