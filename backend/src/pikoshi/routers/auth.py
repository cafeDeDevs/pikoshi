from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..middlewares.logger import TimedRoute
from ..schemas.auth import AuthCodeRequest
from ..services.google_oauth_service import GoogleOAuthService
from ..services.security_service import generate_salt, hash_value, verify_value
from ..services.user_service import create_user, generate_user_profile
from ..utils.auth_cookies import set_auth_cookies
from ..utils.logger import logger

router = APIRouter(prefix="/auth", tags=["auth"], route_class=TimedRoute)


@router.post("/google-signup/")
async def get_google_auth_code(
    request: AuthCodeRequest, db: Session = Depends(get_db)
) -> Response:
    try:
        auth_code = request.code

        data = GoogleOAuthService.get_oauth_config(auth_code)
        user_tokens = await GoogleOAuthService.get_user_tokens(data)
        if not user_tokens:
            raise HTTPException(
                status_code=401, detail="Google Auth Code Not Authorized."
            )

        access_token = user_tokens.get("access_token")
        refresh_token = user_tokens.get("refresh_token")

        user_info = await GoogleOAuthService.get_user_info(access_token)
        if not user_info:
            # TODO: Check refresh_token here and use refresh_token to get new access_token
            # NOTE: Only return 401 if refresh_token also fails here
            raise HTTPException(
                status_code=401, detail="Google Access Token Not Authorized."
            )

        # NOTE: Generates hash based off of user_info.id instead of password
        user_id = user_info.get("id")
        salt = generate_salt()
        user_password = hash_value(user_id, salt)
        new_user = generate_user_profile(user_info, user_password, salt)
        new_user = create_user(db, new_user)
        if not new_user:
            raise HTTPException(
                status_code=400, detail="Email has already been registered."
            )

        response = jsonable_encoder(
            {"message": "User Authenticated, setting credentials."}
        )
        response = JSONResponse(content=response)
        response = set_auth_cookies(response, access_token, refresh_token)

        return response
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error.")
