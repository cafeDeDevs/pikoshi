from fastapi import Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..schemas.user import User
from ..services.user_service import UserService
from ..utils.auth_cookies import remove_auth_cookies, set_auth_cookies
from .jwt_service import JWTAuthService

# TODO: Implement logic re: refreshing of access_token using refresh_token logic
# NOTE: See fastapi-with-google POC for refresh_access_token logic for google-oauth2.
# And also issue new access_token if refresh_token is still good (whether jwt or google-oauth2 token)


class AuthService:
    @staticmethod
    def get_user_by_access_token(
        access_token: str, db: Session = Depends(get_db)
    ) -> User:
        """
        - Verifies both that the JWT access_token has not yet expired,
          and also returns the user_uuid from inside the JWT's sub field.
        - Queries the User DB for a user with that UUID
          and returns the User data from DB.
        """
        verified_token = JWTAuthService.verify_token(access_token)
        user_uuid = verified_token.get("sub")  # type:ignore
        return UserService.get_user_by_uuid(db, user_uuid)

    @staticmethod
    async def authenticate(
        access_token: str,
        db: Session = Depends(get_db),
    ) -> JSONResponse:
        """
        - Grabs the User from the DB based off of UUID returned from JWT access_token.
        - Checks to see of the User exists,
          and if User's `is_active` field is set to True.
        - Returns a HTTP 200 response back to the client if aforementioned is True,
          and returns a HTTP 401 response if either condition is False.
        """
        user = AuthService.get_user_by_access_token(access_token, db)
        if user and user.is_active:
            return JSONResponse(
                status_code=200,
                content={"message": "User Is Authenticated."},
            )
        else:
            raise HTTPException(
                status_code=401, detail="No User Found Within DB or User Not Active"
            )

    @staticmethod
    def set_authenticated_response(access_token, refresh_token) -> Response:
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

    @staticmethod
    async def logout(
        access_token: str,
        db: Session = Depends(get_db),
    ) -> Response:
        """
        - Grabs User from DB using UUID from JWT access_token.
        - Sets the User's `is_active` field in the DB to False.
        - Creates a HTTP 200 OK Response, indicating successful logout.
        - Removes JWT access_token and JWT refresh_token from Client's Cookie Storage.
        - Returns response to Client.
        """
        user = AuthService.get_user_by_access_token(access_token, db)

        UserService.set_user_as_inactive(db, user)
        response = JSONResponse(
            status_code=200, content={"message": "User Logged Out Successfully."}
        )
        response = remove_auth_cookies(response)
        return response
