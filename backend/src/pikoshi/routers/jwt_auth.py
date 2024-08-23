# TODO: Put JWT Auth Route Handlers Here
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..middlewares.logger import TimedRoute
from ..schemas.user import UserInput
from ..services.user_service import (
    create_user,
    generate_user_profile,
    get_user_by_email,
)
from ..utils.auth_cookies import set_auth_cookies
from ..utils.logger import logger

router = APIRouter(prefix="/auth", tags=["auth"], route_class=TimedRoute)


@router.post("/email-registration/")
async def signup_with_google(user_input: UserInput):
    print("user_input :=>", user_input.email)
    jsonMsg = jsonable_encoder({"message": "Hello world"})
    return JSONResponse(jsonMsg)
