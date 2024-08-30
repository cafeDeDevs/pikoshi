import os
from pathlib import Path

import resend
from dotenv import load_dotenv
from fastapi import BackgroundTasks
from pydantic import EmailStr

from ..config.redis_config import redis_instance as redis
from ..services.security_service import generate_sha256_hash

load_dotenv()
resend.api_key = os.environ.get("RESEND_API_KEY")


class EmailService:
    @staticmethod
    def send_signup_email(email: EmailStr, html_content: str) -> None:
        resend.Emails.send(
            {
                "from": "pikoshi@thelastselftaught.dev",
                "to": email,
                "subject": "Complete Pikoshi Sign up",
                "html": html_content,
            }
        )

    @staticmethod
    async def send_transac_email(
        user_input,
        user_email: EmailStr,
        background_tasks: BackgroundTasks,
    ) -> None:
        token = generate_sha256_hash(user_input.email)
        await redis.set(f"signup_token_for_{token}", user_email, ex=600)

        activation_link = f"http://localhost:5173/onboarding/?token={token}"
        template_path = Path("./src/pikoshi/templates/signup_email.html")
        html_template = template_path.read_text()
        html_content = html_template.format(activation_link=activation_link)

        background_tasks.add_task(
            EmailService.send_signup_email, user_input.email, html_content
        )
