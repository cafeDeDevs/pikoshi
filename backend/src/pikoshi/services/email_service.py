import os
from pathlib import Path

import resend
from dotenv import load_dotenv
from fastapi import BackgroundTasks
from pydantic import EmailStr

from ..config.redis_config import redis_instance as redis
from ..services import security_service as SecurityService

load_dotenv()
resend.api_key = os.environ.get("RESEND_API_KEY")


def send_signup_email(email: EmailStr, html_content: str) -> None:
    """
    - Wrapper around Resend Email API.
    - Takes email from Client side /signup form.
    - Sends html_content, which has a cached hashed `token` embedded in link.
      (see templates/signup_email.html)
    """
    resend.Emails.send(
        {
            "from": "pikoshi@thelastselftaught.dev",
            "to": email,
            "subject": "Complete Pikoshi Sign up",
            "html": html_content,
        }
    )


def send_change_password_email(email: EmailStr, html_content: str) -> None:
    """
    - Wrapper around Resend Email API.
    - Takes email from Client side /signup form.
    - Sends html_content, which has a cached hashed `token` embedded in link.
      (see templates/signup_email.html)
    """
    resend.Emails.send(
        {
            "from": "pikoshi@thelastselftaught.dev",
            "to": email,
            "subject": "Reset password for Pikoshi",
            "html": html_content,
        }
    )


async def send_transac_email(
    user_input,
    user_email: EmailStr,
    background_tasks: BackgroundTasks,
) -> None:
    """
    - Generates a hash from user's inputted email and assigns it to `token`.
    - Sets the `token` in the redis cache, expiring in 10 minutes.
    - Creates an `activation_link` for user to follow upon receipt of email.
    - Grabs the email template .html file and assigns it to `template_path`.
    - Converts `template_path` to raw string data and assigns it to `html_template`.
    - Injects the activation link into the `html_template`'s {activation_link}
      template variable.
    - Uses FastAPI's background_tasks.add_task method to invoke send_signup_email.
    - NOTE: Basically, background_tasks makes sure if email is hung up, user is
      given confirmation quickly.
    """
    token = SecurityService.generate_sha256_hash(user_input.email)
    await redis.set(f"signup_token_for_{token}", user_email, ex=600)

    activation_link = f"http://localhost:5173/onboarding/?token={token}"
    template_path = Path("./src/pikoshi/templates/signup_email.html")
    html_template = template_path.read_text()
    html_content = html_template.format(activation_link=activation_link)

    background_tasks.add_task(send_signup_email, user_input.email, html_content)

    # await EmailService.send_password_reset_email(
    #     user.email, reset_link, background_tasks
    # )


async def send_password_reset_email(
    user_input,
    user_email: EmailStr,
    background_tasks: BackgroundTasks,
) -> None:
    """
    TODO: FILL IN DOC STRING LATER
    """

    token = SecurityService.generate_sha256_hash(user_input.email)
    await redis.set(f"change_password_token_for_{token}", user_email, ex=600)

    # TODO: CREATE VIEW FOR CHANGE-PASSWORD
    reset_link = f"http://localhost:5173/change-password/?token={token}"
    template_path = Path("./src/pikoshi/templates/change_password.html")
    html_template = template_path.read_text()
    html_content = html_template.format(reset_link=reset_link)

    background_tasks.add_task(
        send_change_password_email, user_input.email, html_content
    )
