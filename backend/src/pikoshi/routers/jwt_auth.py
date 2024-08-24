from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..config.redis_config import redis_instance as redis
from ..dependencies import get_db
from ..middlewares.logger import TimedRoute
from ..schemas.user import UserInput
from ..services.email_service import send_signup_email
from ..services.security_service import generate_sha256_hash
from ..services.user_service import (
    create_user,
    generate_user_profile,
    get_user_by_email,
)
from ..utils.auth_cookies import set_auth_cookies
from ..utils.logger import logger

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"], route_class=TimedRoute)


@router.post("/email-signup/")
async def signup_with_email(
    user_input: UserInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> Response:
    try:
        user_from_db = get_user_by_email(db, user_input.email)
        if user_from_db:
            raise HTTPException(
                status_code=409, detail="User By That Email Already Exists."
            )

        token = generate_sha256_hash(user_input.email)
        await redis.set(f"email_token_for_{user_input.email}", token)

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
