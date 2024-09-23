from fastapi import Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db_session
from ..schemas.user import User
from ..services import user_service as UserService
from ..utils.auth_cookies import remove_auth_cookies, set_auth_cookies
from . import jwt_service as JWTAuthService


# TODO: Implement logic re: refreshing of access_token using refresh_token logic
# NOTE: See fastapi-with-google POC for refresh_access_token logic for google-oauth2.
# And also issue new access_token if refresh_token is still good (whether jwt or google-oauth2 token)
async def get_user_by_token(
    token: str, db_session: AsyncSession = Depends(get_db_session)
) -> User:
    """
    - Verifies both that the JWT access_token has not yet expired,
      and also returns the user_uuid from inside the JWT's sub field.
    - Queries the User DB for a user with that UUID
      and returns the User data from DB.
    """
    verified_token = JWTAuthService.verify_token(token)
    if verified_token is None:
        return None  # type:ignore
    user_uuid = verified_token.get("sub")  # type:ignore
    return await UserService.get_user_by_uuid(db_session, str(user_uuid))


async def authenticate(
    access_token: str,
    refresh_token: str,
    db_session: AsyncSession = Depends(get_db_session),
) -> JSONResponse:
    """
    - Grabs the User from the DB based off of UUID returned from JWT access_token.
    - Checks to see if the User exists and if User's `is_active` field is set to True.
    - Returns a HTTP 200 response back to the client if the aforementioned is True,
      and returns a HTTP 401 response if either condition is False.
    """
    user = await get_user_by_token(access_token, db_session)

    if not user or not user.is_active:
        user = await get_user_by_token(refresh_token, db_session)

        if user and user.is_active:
            new_access_token = JWTAuthService.create_access_token(user.uuid)

            response = set_authenticated_response(new_access_token, refresh_token)

            return response

        else:
            raise HTTPException(
                status_code=401, detail="No valid authentication tokens provided."
            )

    return JSONResponse(
        status_code=200,
        content={"message": "User Is Authenticated."},
    )


def set_authenticated_response(access_token, refresh_token) -> JSONResponse:
    """
    - Appends HTTP Only Secure Cookies with JWT access_token
      and JWT refresh_token in response.
    - Returns reponse with appended Auth Cookies.
    """
    response = JSONResponse(
        status_code=200,
        content={"message": "User Authenticated, setting credentials."},
    )
    response = set_auth_cookies(response, access_token, refresh_token)
    return response


async def logout(
    access_token: str,
    db_session: AsyncSession = Depends(get_db_session),
) -> Response:
    """
    - Grabs User from DB using UUID from JWT access_token.
    - Sets the User's `is_active` field in the DB to False.
    - Creates a HTTP 200 OK Response, indicating successful logout.
    - Removes JWT access_token and JWT refresh_token from Client's Cookie Storage.
    - Returns response to Client.
    """
    user = await get_user_by_token(access_token, db_session)

    await UserService.set_user_as_inactive(db_session, user)
    response = JSONResponse(
        status_code=200, content={"message": "User Logged Out Successfully."}
    )
    response = remove_auth_cookies(response)
    return response
