import os

import resend
from dotenv import load_dotenv

load_dotenv()
resend.api_key = os.environ.get("RESEND_API_KEY")


def send_signup_email(email: str, html_content: str) -> None:
    resend.Emails.send(
        {
            "from": "pikoshi@thelastselftaught.dev",
            "to": email,
            "subject": "Complete Pikoshi Sign up",
            "html": html_content,
        }
    )
