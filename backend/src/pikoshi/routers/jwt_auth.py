from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from jwt.exceptions import PyJWTError
from sqlalchemy.orm import Session

from ..config.redis_config import redis_instance as redis
from ..dependencies import get_db
from ..middlewares.logger import TimedRoute
from ..schemas.auth import TokenRequest
from ..schemas.user import UserInput, UserInputEmailPass, UserInputPass
from ..services.auth_service import AuthService
from ..services.email_service import EmailService
from ..services.exception_handler_service import ExceptionService
from ..services.jwt_service import JWTAuthService
from ..services.user_service import get_user_by_email
from ..utils.logger import logger

router = APIRouter(prefix="/auth", tags=["auth"], route_class=TimedRoute)


@router.post("/email-signup/")
async def signup_with_email(
    user_input: UserInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> Response:
    try:
        user_email = user_input.email
        user_from_db = get_user_by_email(db, user_email)
        if user_from_db:
            raise HTTPException(
                status_code=409, detail="Email has already been registered."
            )

        await EmailService.send_transac_email(user_input, user_email, background_tasks)

        jsonMsg = jsonable_encoder({"message": "email has been sent"})
        return JSONResponse(status_code=200, content=jsonMsg)
    except Exception as e:
        return ExceptionService.handle_generic_exception(e)


@router.post("/check-token/")
async def check_token(request: TokenRequest) -> Response:
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
    user_info: UserInputPass, db: Session = Depends(get_db)
) -> Response:
    try:
        user_email = await redis.get(f"signup_token_for_{user_info.token}")
        if not user_email:
            logger.error(f"Token not found or expired: {user_info.token}")
            raise HTTPException(status_code=401, detail="Token not found or expired.")
        await redis.delete(f"signup_token_for_{user_info.token}")

        user_tokens = JWTAuthService.get_user_tokens()
        access_token = user_tokens["access_token"]
        refresh_token = user_tokens["refresh_token"]

        await JWTAuthService.signup_user_with_email(
            user_info, user_email, access_token, db
        )

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
    user_info: UserInputEmailPass, db: Session = Depends(get_db)
) -> Response:
    try:
        user_tokens = JWTAuthService.get_user_tokens()
        access_token = user_tokens["access_token"]
        refresh_token = user_tokens["refresh_token"]

        await JWTAuthService.authenticate_user_with_jwt(user_info, access_token, db)

        response = AuthService.set_authenticated_response(access_token, refresh_token)
        return response
    except HTTPException as http_e:
        return ExceptionService.handle_http_exception(http_e)
    except PyJWTError as jwt_e:
        return ExceptionService.handle_jwt_exception(jwt_e)
    except Exception as e:
        return ExceptionService.handle_generic_exception(e)
