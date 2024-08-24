from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..config.redis_config import redis_instance as redis
from ..dependencies import get_db
from ..middlewares.logger import TimedRoute
from ..schemas.auth import TokenRequest
from ..schemas.user import UserInput, UserInputPass
from ..services.email_service import send_signup_email
from ..services.jwt_service import JWTAuthService
from ..services.security_service import (
    generate_salt,
    generate_sha256_hash,
    hash_value,
    verify_value,
)
from ..services.user_service import (
    create_user,
    generate_user_profile,
    get_user_by_email,
)
from ..utils.auth_cookies import set_auth_cookies
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

        token = generate_sha256_hash(user_input.email)
        await redis.set(f"signup_token_for_{token}", user_email, ex=600)

        activation_link = f"http://localhost:5173/onboarding/?token={token}"
        template_path = Path("./src/pikoshi/templates/signup_email.html")
        html_template = template_path.read_text()
        html_content = html_template.format(activation_link=activation_link)

        background_tasks.add_task(send_signup_email, user_input.email, html_content)

        jsonMsg = jsonable_encoder({"message": "email has been sent"})
        return JSONResponse(status_code=200, content=jsonMsg)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error.")


@router.post("/check-token/")
async def check_token(request: TokenRequest) -> Response:
    try:
        token = request.token
        user_email = await redis.get(f"signup_token_for_{token}")
        if not user_email:
            logger.error(f"Token not found or expired: {token}")
            raise HTTPException(status_code=401, detail="Token not found or expired.")
        return JSONResponse(status_code=200, content={"message": "Token is validated."})
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error.")


@router.post("/email-onboarding/")
async def email_onboarding(user_info: UserInputPass, db: Session = Depends(get_db)):
    try:
        user_email = await redis.get(f"signup_token_for_{user_info.token}")
        if not user_email:
            logger.error(f"Token not found or expired: {user_info.token}")
            raise HTTPException(status_code=401, detail="Token not found or expired.")

        salt = generate_salt()
        user_name = user_info.username
        user_password = hash_value(user_info.password, salt)
        new_user = generate_user_profile(user_name, user_password, user_email, salt)
        new_user = create_user(db, new_user)
        if not new_user:
            raise HTTPException(
                status_code=409, detail="Email has already been registered."
            )

        user_tokens = JWTAuthService.get_user_tokens()
        access_token = user_tokens["access_token"]
        refresh_token = user_tokens["refresh_token"]

        response = jsonable_encoder(
            {"message": "User Authenticated, setting credentials."}
        )
        response = JSONResponse(status_code=200, content=response)
        response = set_auth_cookies(response, access_token, refresh_token)
        return response
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error.")
