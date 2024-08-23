from pydantic import BaseModel


class AuthCodeRequest(BaseModel):
    code: str
