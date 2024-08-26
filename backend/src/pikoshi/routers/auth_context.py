from typing import Annotated

import jwt
from fastapi import APIRouter, Cookie, HTTPException, Response
from fastapi.responses import JSONResponse

from ..middlewares.logger import TimedRoute
from ..services.jwt_service import ALGORITHM, SECRET_KEY, JWTAuthService
from ..utils.logger import logger

router = APIRouter(prefix="/auth", tags=["auth"], route_class=TimedRoute)


# TODO: Put main authorization logic here:
# Check against Google (consider using the two . used in phlint project)
# Check JWTs are not expired
# Inauthenticate and log out if user's tokens no longer good.


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
) -> Response:
    try:
        if not access_token and not refresh_token:
            raise HTTPException(
                status_code=401,
                detail="No Authentication Tokens Submitted For Authentication.",
            )
        # TODO: Implement logic re: refreshing of
        # access_token using refresh_token logic
        if not JWTAuthService.is_jwt(access_token):
            print("is google-oauth2 access token")
            #  authenticate_google_oauth_access_token(access_token)
        else:
            decoded_access_token = jwt.decode(
                str(access_token),
                SECRET_KEY,
                algorithms=[ALGORITHM],
            )
            # NOTE: Consider using UUID instead of encrypted email as
            # redis value associated with jwt sub?

            # TODO: Once decoded decrypt encrypted email
            # str here, and check if is in redis
            if not decoded_access_token:
                raise HTTPException(
                    status_code=401, detail="Access Token Corrupted Or No Longer Valid."
                )

            print("decoded_access_token :=>", decoded_access_token.get("sub"))

            #  authenticate_jwt_access_token(access_token)

        return JSONResponse(status_code=200, content={"message": "AOKay!"})
    except HTTPException as http_e:
        raise HTTPException(status_code=http_e.status_code, detail=http_e.detail)
    except jwt.exceptions.PyJWTError as jwt_e:
        raise HTTPException(status_code=401, detail=jwt_e)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error.")
