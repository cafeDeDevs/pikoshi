from typing import Annotated

import jwt
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..config.redis_config import redis_instance as redis
from ..dependencies import get_db
from ..middlewares.logger import TimedRoute
from ..services.google_oauth_service import GoogleOAuthService
from ..services.jwt_service import JWTAuthService
from ..services.user_service import get_user, get_user_by_email
from ..utils.logger import logger

router = APIRouter(prefix="/auth", tags=["auth"], route_class=TimedRoute)


# NOTE: See fastapi-with-google POC for refresh_access_token logic for google-oauth2.
# And also issue new access_token if refresh_token is still good (whether jwt or google-oauth2 token)

# TODO: JWTs should hold onto hash that represents user's email
# Email is stored in redis cache, where jwt hash is key, email is value
# Find user in db by email and set is_active status to false if no longer
# authenticated (i.e. logged out)


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
        # TODO: Implement logic re: refreshing of access_token using refresh_token logic
        if JWTAuthService.is_jwt(access_token):
            JWTAuthService.verify_token(str(access_token))
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

        elif not JWTAuthService.is_jwt(access_token):
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

        raise HTTPException(
            status_code=401,
            detail="Tokens passed are neither JWTs nor Google OAuth2 tokens.",
        )
    except HTTPException as http_e:
        logger.error(f"An error involving HTTP Cookies occurred: {str(http_e)}")
        return JSONResponse(
            status_code=http_e.status_code, content={"message": f"{http_e.detail}"}
        )
    except jwt.exceptions.PyJWTError as jwt_e:
        logger.error(f"An error involving JWT occurred: {str(jwt_e)}")
        return JSONResponse(
            status_code=401,
            content={"message": f"JWT error: {str(jwt_e)}"},
        )
    except ValueError as ve:
        logger.error(f"Value error occurred: {str(ve)}")
        return JSONResponse(
            status_code=401,
            content={"message": str(ve)},
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error."}
        )
