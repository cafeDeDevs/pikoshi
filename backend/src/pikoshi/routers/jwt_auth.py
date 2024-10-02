from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException,
                     Response)
from fastapi.responses import JSONResponse
from jwt.exceptions import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.redis_config import redis_instance as redis
from ..dependencies import get_db_session
from ..middlewares.logger import TimedRoute
from ..schemas.auth import TokenRequest
from ..schemas.user import UserInput, UserInputEmailPass, UserInputPass
from ..services import auth_service as AuthService
from ..services import email_service as EmailService
from ..services import exception_handler_service as ExceptionService
from ..services import jwt_service as JWTAuthService
from ..services import user_service as UserService
from ..utils.logger import logger

router = APIRouter(prefix="/auth", tags=["auth"], route_class=TimedRoute)


@router.post("/email-signup/")
async def signup_with_email(
    user_input: UserInput,
    background_tasks: BackgroundTasks,
    db_session: AsyncSession = Depends(get_db_session),
) -> Response:
    """
    - Grabs the user's email from the Client's /signup input form.
    - Checks to see if the user's email already exists within the DB.
    - If the user already exists, throw a 409 response back to the Client.
    - Otherwise Send a Transactional Email to the User using Resend,
      see EmailService.send_transac_email for details.
    - NOTE: send_transac_email sets hash token and user_email in redis cache.
    """
    try:
        user_email = user_input.email
        user_from_db = await UserService.get_user_by_email(db_session, user_email)
        if user_from_db:
            raise HTTPException(
                status_code=409, detail="Email has already been registered."
            )

        await EmailService.send_transac_email(user_input, user_email, background_tasks)

        return JSONResponse(
            status_code=200, content={"message": "Email has been sent."}
        )
    except Exception as e:
        return ExceptionService.handle_generic_exception(e)


@router.post("/check-token/")
async def check_token(request: TokenRequest) -> Response:
    """
    - Grabs the hashed token that was in the Client Side URL
      (/onboarding?token=) from the request.
    - Checks the redis cache to ensure the user initially signed
      up via email via /email-signup/.
    - If the redis cache does not have record of the token:
      - The user either waited too long...
      - Or never signed up to begin with...
      - And we throw a 401 HTTP Response back to them
        (i.e they need to sign up).
    - Otherwise there is a record of them in the redis cache and
      we throw an HTTP 200 OK back to the Client.
    """
    try:
        token = request.token
        user_email = await redis.get(f"signup_token_for_{token}")
        if not user_email:
            raise HTTPException(status_code=401, detail="Token not found or expired.")

        return JSONResponse(status_code=200, content={"message": "Token is validated."})
    except Exception as e:
        return ExceptionService.handle_generic_exception(e)


@router.post("/email-onboarding/")
async def email_onboarding(
    user_info: UserInputPass, db_session: AsyncSession = Depends(get_db_session)
) -> Response:
    """
    - After the User fills out the onboarding form
      (i.e. user establishes a name, email, password),
      - We check the redis cache to be sure they didn't take too long
        to fill out the form..
      - If the user took too long, we throw back a HTTP 401 to the Client.
      - Otherwise, the token is removed from the redis cache.
    - A New User is then establised in the DB.
    - And We grab the uuid from the New User from the DB.
    - We then establish a new JWT access_token and a new JWT refresh_token
      with the New User's UUID inside them.
    - Sets the JWT access_token and JWT refresh_token in HTTP-Only Secure cookies,
      and sends them back to Client.
    """
    try:
        user_email = await redis.get(f"signup_token_for_{user_info.token}")
        if not user_email:
            logger.error(f"Token not found or expired: {user_info.token}")
            raise HTTPException(status_code=401, detail="Token not found or expired.")
        await redis.delete(f"signup_token_for_{user_info.token}")

        new_user = await JWTAuthService.signup_user_with_email(
            user_info, user_email, db_session, method="email"
        )
        user_uuid = new_user.uuid

        user_tokens = JWTAuthService.get_user_tokens(user_uuid)
        access_token = user_tokens["access_token"]
        refresh_token = user_tokens["refresh_token"]

        response = AuthService.set_authenticated_response(access_token, refresh_token)
        return response
    except HTTPException as http_e:
        return ExceptionService.handle_http_exception(http_e)
    except PyJWTError as jwt_e:
        return ExceptionService.handle_jwt_exception(jwt_e)
    except Exception as e:
        return ExceptionService.handle_generic_exception(e)


@router.post("/email-login/")
async def email_login(
    user_info: UserInputEmailPass, db_session: AsyncSession = Depends(get_db_session)
) -> Response:
    """
    - Grabs the user_info from the Client side form
      (i.e. user's inputted email and password).
    - Uses the user_info to authenticate user (see `authenticate_user_with_jwt`),
      which returns the User data from the DB.
    - Uses the returned User Data from the DB to create JWT access_token and JWT
      refresh_token with the User's UUID inside them.
    - Sets the JWT access_token and JWT refresh_token in HTTP-Only Secure cookies,
      and sends them back to Client.
    """
    try:
        user = await JWTAuthService.authenticate_user_with_jwt(user_info, db_session)
        user_tokens = JWTAuthService.get_user_tokens(user.uuid)
        access_token = user_tokens["access_token"]
        refresh_token = user_tokens["refresh_token"]

        response = AuthService.set_authenticated_response(access_token, refresh_token)
        return response
    except HTTPException as http_e:
        return ExceptionService.handle_http_exception(http_e)
    except PyJWTError as jwt_e:
        return ExceptionService.handle_jwt_exception(jwt_e)
    except Exception as e:
        return ExceptionService.handle_generic_exception(e)


@router.post("/forgot-password/")
async def forgot_password(
    email: str,
    background_tasks: BackgroundTasks,
    db_session: AsyncSession = Depends(get_db_session),
):
    """
    Handles the Forgot Password functionality:
    - Checks if the user exists in the database.
    - If the user signed up via OAuth2, return a 400 error.
    - Otherwise, sends a password reset email with a unique token.
    """
    try:
        user = await UserService.get_user_by_email(db_session, email)
        if not user:
            raise HTTPException(status_code=400, detail="User not found.")

        if user.signed_up_method == "oauth2":
            raise HTTPException(
                status_code=400,
                detail="Users signed up via OAuth2 cannot reset their password.",
            )

        token = str(uuid4())
        await redis.set(f"change_password_token_for_{token}", user.email, ex=600)
        # Expiration time: 10 minutes

        # Send a password reset email with the token
        reset_link = f"http://yourfrontend.com/reset-password?token={token}"
        await EmailService.send_password_reset_email(
            user.email, reset_link, background_tasks
        )

        return {"message": "Password reset email sent."}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred while processing the request."
        )

# this is a test commit