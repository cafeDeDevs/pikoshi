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
