from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db_session
from ..middlewares.logger import TimedRoute
from ..schemas.auth import AuthCodeRequest
from ..services.auth_service import AuthService
from ..services.exception_handler_service import ExceptionService
from ..services.google_oauth_service import GoogleOAuthService
from ..services.jwt_service import JWTAuthService

router = APIRouter(prefix="/auth", tags=["auth"], route_class=TimedRoute)


@router.post("/google-signup/")
async def signup_with_google(
    request: AuthCodeRequest, db_session: AsyncSession = Depends(get_db_session)
) -> Response:
    """
    - Grabs the auth-code from
      SolidJS/GoogleOAuth2 Package (hand-written on front end).
    - Grabs User's OAuth access_token and refresh_token (prefixed here with `google_`).
    - Grabs User's Information (i.e. google id, email, name, etc.) using google_access_token.
    - Signs Up User in database and returns new User data from DB.
    - Grabs the new User's UUID and puts it inside of JWT access_token and refresh_token.
    - Sets the JWT access_token and JWT refresh_token in HTTP-Only Secure cookies,
      and sends them back to Client.
    """
    try:
        auth_code = request.code
        user_tokens = await GoogleOAuthService.get_user_tokens(auth_code)
        google_access_token = str(user_tokens.get("access_token"))
        # TODO: Use google_refresh_token to refresh google access_token
        # google_refresh_token = str(user_tokens.get("refresh_token"))

        user_info = await GoogleOAuthService.get_user_info(google_access_token)
        new_user = await GoogleOAuthService.signup_user_with_google(
            user_info, db_session
        )
        user_uuid = new_user.uuid
        user_tokens = JWTAuthService.get_user_tokens(user_uuid)
        access_token = user_tokens["access_token"]
        refresh_token = user_tokens["refresh_token"]

        response = AuthService.set_authenticated_response(access_token, refresh_token)

        return response
    except HTTPException as http_e:
        return ExceptionService.handle_http_exception(http_e)
    except ValueError as ve:
        return ExceptionService.handle_value_exception(ve)
    except Exception as e:
        return ExceptionService.handle_generic_exception(e)


@router.post("/google-login/")
async def login_with_google(
    request: AuthCodeRequest, db_session: AsyncSession = Depends(get_db_session)
) -> Response:
    """
    - Grabs the auth-code from
      SolidJS/GoogleOAuth2 Package (hand-written on front end).
    - Grabs User's OAuth access_token and refresh_token (prefixed here with `google_`).
    - Grabs User's Information (i.e. google id, email, name, etc.) using google_access_token.
    - Uses the returned User's Information to query the DB by email and return the User from DB.
    - Authenticates the User By Comparing User's Google ID against DB User Password.
    - Grabs new JWTs with user's UUID inside both JWT access_token and JWT refresh_token.
    - Sets the JWT access_token and JWT refresh_token in HTTP-Only Secure cookies,
      and sends them back to Client.
    """
    try:
        auth_code = request.code
        user_tokens = await GoogleOAuthService.get_user_tokens(auth_code)
        google_access_token = str(user_tokens.get("access_token"))
        # TODO: Use google_refresh_token to refresh google access_token
        #  google_refresh_token = str(user_tokens.get("refresh_token"))

        user_info = await GoogleOAuthService.get_user_info(google_access_token)
        user_from_db = await GoogleOAuthService.get_user_by_email_from_db(
            user_info, db_session
        )

        user_tokens = await GoogleOAuthService.authenticate_user_with_google(
            user_info, user_from_db, db_session
        )
        access_token = user_tokens["access_token"]
        refresh_token = user_tokens["refresh_token"]

        response = AuthService.set_authenticated_response(access_token, refresh_token)

        return response
    except HTTPException as http_e:
        return ExceptionService.handle_http_exception(http_e)
    except ValueError as ve:
        return ExceptionService.handle_value_exception(ve)
    except Exception as e:
        return ExceptionService.handle_generic_exception(e)
