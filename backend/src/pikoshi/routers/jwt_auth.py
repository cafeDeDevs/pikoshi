from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

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

router = APIRouter(prefix="/auth", tags=["auth"], route_class=TimedRoute)


@router.post("/email-signup/")
async def signup_with_google(user_input: UserInput, background_tasks: BackgroundTasks):
    # TODO: Check DB to be sure user doesn't exist there, return HTTP error if user email already exists
    # TODO: Put Hash token in redis cache
    token = generate_sha256_hash(user_input.email)
    activation_link = f"http://localhost:5173/onboarding/?token={token}"

    template_path = Path("./src/pikoshi/templates/signup_email.html")
    html_template = template_path.read_text()
    html_content = html_template.format(activation_link=activation_link)

    background_tasks.add_task(send_signup_email, user_input.email, html_content)

    # TODO: Check if email is in DB and return HTTP ERR if so
    # Send Transac Email that returns user back to frontend route with token in URL
    # TODO: Set up redis cache to hold onto token to be checked in URL
    jsonMsg = jsonable_encoder({"message": "email has been sent"})
    return JSONResponse(status_code=200, content=jsonMsg)
