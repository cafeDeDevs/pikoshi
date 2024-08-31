from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..config.redis_config import redis_instance as redis
from ..dependencies import get_db
from ..middlewares.logger import TimedRoute

router = APIRouter(prefix="/gallery", tags=["gallery"], route_class=TimedRoute)


@router.post("/default/")
async def get_default_gallery(
    access_token: Annotated[str | None, Cookie()] = None,
    refresh_token: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
) -> Response:
    return JSONResponse(status_code=200, content={"message": "Hello World!"})
