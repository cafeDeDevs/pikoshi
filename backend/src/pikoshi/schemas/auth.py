from pydantic import BaseModel


class AuthCodeRequest(BaseModel):
    code: str


class TokenRequest(BaseModel):
    token: str
