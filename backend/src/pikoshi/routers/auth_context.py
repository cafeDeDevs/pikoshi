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
    """
    - Authenticates user by verifying UUID contents of access_token JWT
    """
    try:
        if not access_token or not refresh_token:
            raise HTTPException(
                status_code=401,
                detail="No Authentication Tokens Submitted For Authentication.",
            )
        return await AuthService.authenticate(access_token, db)

    except HTTPException as http_e:
        return ExceptionService.handle_http_exception(http_e)
    except PyJWTError as jwt_e:
        return ExceptionService.handle_jwt_exception(jwt_e)
    except ValueError as ve:
        return ExceptionService.handle_value_exception(ve)
    except Exception as e:
        return ExceptionService.handle_generic_exception(e)


@router.post("/auth-logout/")
async def auth_logout(
    access_token: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
) -> Response:
    """
    - Logs Out User by removing their JWT tokens from HTTP only cookies
      and Sets User's `is_active` field in DB to False.
    """
    try:
        response = await AuthService.logout(str(access_token), db)
        return response
    except Exception as e:
        return ExceptionService.handle_generic_exception(e)
