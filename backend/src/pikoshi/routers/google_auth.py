from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..middlewares.logger import TimedRoute
from ..schemas.auth import AuthCodeRequest
from ..services.exception_handler_service import ExceptionService
from ..services.google_oauth_service import GoogleOAuthService

router = APIRouter(prefix="/auth", tags=["auth"], route_class=TimedRoute)


@router.post("/google-signup/")
async def signup_with_google(
    request: AuthCodeRequest, db: Session = Depends(get_db)
) -> Response:
    try:
        auth_code = request.code
        user_tokens = await GoogleOAuthService.get_user_tokens(auth_code)
        access_token = str(user_tokens.get("access_token"))
        refresh_token = str(user_tokens.get("refresh_token"))

        user_info = await GoogleOAuthService.get_user_info(access_token)
        await GoogleOAuthService.signup_user_with_google(user_info, access_token, db)

        response = GoogleOAuthService.set_authenticated_response(
            access_token, refresh_token
        )

        return response
    except HTTPException as http_e:
        return ExceptionService.handle_http_exception(http_e)
    except ValueError as ve:
        return ExceptionService.handle_value_exception(ve)
    except Exception as e:
        return ExceptionService.handle_generic_exception(e)


@router.post("/google-login/")
async def login_with_google(
    request: AuthCodeRequest, db: Session = Depends(get_db)
) -> Response:
    try:
        auth_code = request.code
        user_tokens = await GoogleOAuthService.get_user_tokens(auth_code)
        access_token = str(user_tokens.get("access_token"))
        refresh_token = str(user_tokens.get("refresh_token"))

        user_info = await GoogleOAuthService.get_user_info(access_token)
        user_from_db = GoogleOAuthService.get_user_by_email_from_db(user_info, db)

        await GoogleOAuthService.authenticate_user_with_google(
            user_info, user_from_db, access_token, db
        )

        response = GoogleOAuthService.set_authenticated_response(
            access_token, refresh_token
        )

        return response
    except HTTPException as http_e:
        return ExceptionService.handle_http_exception(http_e)
    except ValueError as ve:
        return ExceptionService.handle_value_exception(ve)
    except Exception as e:
        return ExceptionService.handle_generic_exception(e)
