from datetime import datetime, timedelta, timezone

from fastapi import Response


def set_auth_cookie(response: Response, key: str, value: str, expires: int) -> Response:
    expiration_time = datetime.now(timezone.utc) + timedelta(seconds=expires)
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        samesite="none",
        secure=True,
        path="/",
        expires=expiration_time,
    )
    return response


# NOTE: Sets default access_token and refresh_token cookies
# Both Google OAuth2 and JWT Auth Cookies set here
# NOTE: The expiry times on both types of tokens expire 1 hour for access_token and 24 hours for refresh_token (as per Google OAuth2 defaults)
def set_auth_cookies(
    response: Response, access_token: str, refresh_token: str
) -> Response:
    response = set_auth_cookie(response, "access_token", access_token, 3600)
    response = set_auth_cookie(response, "refresh_token", refresh_token, 86400)
    return response
