from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..middlewares.logger import TimedRoute
from ..schemas.auth import AuthCodeRequest
from ..schemas.user import User, UserCreate
from ..services.google_oauth_service import GoogleOAuthService
from ..services.user_service import create_user, get_user_by_email
from ..utils.auth_cookies import set_auth_cookie

router = APIRouter(prefix="/auth", tags=["auth"], route_class=TimedRoute)


@router.post("/google-signup/")
async def get_google_auth_code(request: AuthCodeRequest):
    auth_code = request.code

    data = GoogleOAuthService.get_oauth_config(auth_code)
    user_info = await GoogleOAuthService.get_user_info(data)

    if not user_info:
        raise HTTPException(status_code=401, detail="Google Auth Code Not Authorized.")

    access_token = user_info.get("access_token")
    refresh_token = user_info.get("refresh_token")

    response = jsonable_encoder({"message": "User Authenticated, setting credentials."})
    response = JSONResponse(content=response)
    response = set_auth_cookie(response, "access_token", access_token)
    response = set_auth_cookie(response, "refresh_token", refresh_token)

    return response
