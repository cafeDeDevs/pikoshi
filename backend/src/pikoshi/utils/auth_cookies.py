from fastapi import Response


def set_auth_cookie(response: Response, key: str, value: str) -> Response:
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        samesite="none",
        secure=True,
        path="/",
    )
    return response


def set_auth_cookies(
    response: Response, access_token: str, refresh_token: str
) -> Response:
    response = set_auth_cookie(response, "access_token", access_token)
    response = set_auth_cookie(response, "refresh_token", refresh_token)
    return response
