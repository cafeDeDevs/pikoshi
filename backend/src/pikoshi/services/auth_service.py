from fastapi import Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..services.user_service import get_user_by_uuid, set_user_as_inactive
from ..utils.auth_cookies import remove_auth_cookies, set_auth_cookies
from .jwt_service import JWTAuthService

# TODO: Implement logic re: refreshing of access_token using refresh_token logic
# NOTE: See fastapi-with-google POC for refresh_access_token logic for google-oauth2.
# And also issue new access_token if refresh_token is still good (whether jwt or google-oauth2 token)


class AuthService:
    @staticmethod
    async def authenticate(
        access_token: str,
        db: Session = Depends(get_db),
    ) -> JSONResponse:
        verified_token = JWTAuthService.verify_token(access_token)
        user_uuid = verified_token.get("sub")  # type:ignore
        user = get_user_by_uuid(db, user_uuid)
        if user and user.is_active:  # type:ignore
            return JSONResponse(
                status_code=200,
                content={"message": "User Is Authenticated With JWTs."},
            )
        else:
            raise HTTPException(
                status_code=401, detail="No User Found Within DB or User Not Active"
            )

    @staticmethod
    def set_authenticated_response(access_token, refresh_token) -> Response:
        response = jsonable_encoder(
            {"message": "User Authenticated, setting credentials."}
        )
        response = JSONResponse(status_code=200, content=response)
        response = set_auth_cookies(response, access_token, refresh_token)
        return response

    @staticmethod
    async def logout(
        access_token: str,
        db: Session = Depends(get_db),
    ) -> Response:
        verified_token = JWTAuthService.verify_token(access_token)
        user_uuid = verified_token.get("sub")  # type:ignore
        user = get_user_by_uuid(db, user_uuid)

        set_user_as_inactive(db, user)
        response = JSONResponse(
            status_code=200, content={"message": "User Logged Out Successfully."}
        )
        response = remove_auth_cookies(response)
        return response
