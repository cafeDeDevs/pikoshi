from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from jwt.exceptions import PyJWTError
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..middlewares.logger import TimedRoute
from ..services.auth_service import AuthService
from ..services.exception_handler_service import ExceptionService

router = APIRouter(prefix="/auth", tags=["auth"], route_class=TimedRoute)


@router.post("/auth-context/")
async def check_auth_context(
    access_token: Annotated[str | None, Cookie()] = None,
    refresh_token: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
) -> Response:
    try:
        if not access_token or not refresh_token:
            raise HTTPException(
                status_code=401,
                detail="No Authentication Tokens Submitted For Authentication.",
            )
        if AuthService.is_jwt(access_token):
            return await AuthService.authenticate_jwt(access_token, db)

        elif AuthService.is_google_oauth_token(access_token):
            return await AuthService.authenticate_google_oauth(access_token, db)

        raise HTTPException(
            status_code=401,
            detail="Tokens passed are neither JWTs nor Google OAuth2 tokens.",
        )

    except HTTPException as http_e:
        return ExceptionService.handle_http_exception(http_e)
    except PyJWTError as jwt_e:
        return ExceptionService.handle_jwt_exception(jwt_e)
    except ValueError as ve:
        return ExceptionService.handle_value_exception(ve)
    except Exception as e:
        return ExceptionService.handle_generic_exception(e)
