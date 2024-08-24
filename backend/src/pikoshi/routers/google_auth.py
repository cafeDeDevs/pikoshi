from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..middlewares.logger import TimedRoute
from ..schemas.auth import AuthCodeRequest
from ..services.google_oauth_service import GoogleOAuthService
from ..services.security_service import generate_salt, hash_value, verify_value
from ..services.user_service import (
    create_user,
    generate_user_profile,
    get_user_by_email,
)
from ..utils.auth_cookies import set_auth_cookies
from ..utils.logger import logger

router = APIRouter(prefix="/auth", tags=["auth"], route_class=TimedRoute)


@router.post("/google-signup/")
async def signup_with_google(
    request: AuthCodeRequest, db: Session = Depends(get_db)
) -> Response:
    try:
        auth_code = request.code
        user_tokens = await GoogleOAuthService.get_user_tokens(auth_code)
        if not user_tokens:
            raise HTTPException(
                status_code=401, detail="Google Auth Code Not Authorized."
            )

        access_token = user_tokens.get("access_token")
        refresh_token = user_tokens.get("refresh_token")

        user_info = await GoogleOAuthService.get_user_info(access_token)
        if not user_info:
            raise HTTPException(
                status_code=401, detail="Google Access Token Not Authorized."
            )

        # NOTE: Generates hash based off of user_info.id instead of password
        user_id = user_info.get("id")
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

        response = jsonable_encoder(
            {"message": "User Authenticated, setting credentials."}
        )
        response = JSONResponse(status_code=200, content=response)
        response = set_auth_cookies(response, access_token, refresh_token)

        return response
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error.")


@router.post("/google-login/")
async def login_with_google(
    request: AuthCodeRequest, db: Session = Depends(get_db)
) -> Response:
    try:
        auth_code = request.code

        user_tokens = await GoogleOAuthService.get_user_tokens(auth_code)
        if not user_tokens:
            raise HTTPException(
                status_code=401, detail="Google Auth Code Not Authorized."
            )

        access_token = user_tokens.get("access_token")
        refresh_token = user_tokens.get("refresh_token")

        user_info = await GoogleOAuthService.get_user_info(access_token)
        if not user_info:
            raise HTTPException(
                status_code=401, detail="Google Access Token Not Authorized."
            )

        user_email = user_info.get("email")
        user_from_db = get_user_by_email(db, user_email)
        if not user_from_db:
            raise HTTPException(status_code=400, detail="No User By That Email Found")

        # Generates a hash from the user_id (from the google oauth code)
        # and the user_salt (from the DB)
        # and then compares the hash generated to the hash in the DB (user_password)
        user_id = user_info.get("id")
        user_password = str(user_from_db.password)
        user_salt = str(user_from_db.salt)
        user_is_verified = verify_value(user_id, user_password, user_salt)

        if not user_is_verified:
            raise HTTPException(status_code=401, detail="Hashes in DB do not match")

        # TODO: Set user.is_active to true in DB, and update user.last_login to now

        response = jsonable_encoder(
            {"message": "User Authenticated, setting credentials."}
        )
        response = JSONResponse(content=response)
        response = set_auth_cookies(response, access_token, refresh_token)

        return response
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error.")


# TODO: Create Generic Authentication Route That will test against Google OAuth2
# Token AND JWT Token.
# NOTE: Route MUST check access_token first, then if that fails, check refresh_token
# NOTE: If refresh_token still good, request new access_token from Auth Authority (Google OR JWT)
