from datetime import datetime, timedelta, timezone

from fastapi import Response


def set_s3_continuation_token(response: Response, continuation_token: str) -> Response:
    """
    - Sets the s3 continuation_token in an HTTP Only Secure Cookie.
    """
    response.set_cookie(
        key="s3_continuation_token",
        value=continuation_token,
        httponly=True,
        samesite="none",
        secure=True,
        path="/",
    )
    return response


def set_auth_cookie(response: Response, key: str, value: str, expires: int) -> Response:
    """
    - Creates an HTTP Only Secure Cookie.
    - NOTE: For use with JWT access_token and JWT refresh_token.
    """
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
    """
    - Sets both JWT access_token and JWT refresh_token in cookie headers,
      establishing them with respective expiration times that should
      reflect JWT's expiration times.
    - Returns response with auth cookies.
    """
    response = set_auth_cookie(response, "access_token", access_token, 3600)
    response = set_auth_cookie(response, "refresh_token", refresh_token, 86400)
    return response


def remove_auth_cookies(response: Response) -> Response:
    """
    - Deletes both JWT access_token and JWT refresh_token from cookie headers.
    - Returns response without auth cookies.
    """
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    response.delete_cookie(key="s3_continuation_token")
    return response
