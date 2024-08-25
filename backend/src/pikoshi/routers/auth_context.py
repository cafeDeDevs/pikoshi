from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from fastapi.responses import JSONResponse

from ..middlewares.logger import TimedRoute

router = APIRouter(prefix="/auth", tags=["auth"], route_class=TimedRoute)


# TODO: Put main authorization logic here:
# Check against Google (consider using the two . used in phlint project)
# Check JWTs are not expired
# Inauthenticate and log out if user's tokens no longer good.


# NOTE: See fastapi-with-google POC for refresh_access_token logic for google-oauth2.
# And also issue new access_token if refresh_token is still good (whether jwt or google-oauth2 token)


# TODO: JWTs should hold onto hash that represents user's email
# Email is stored in redis cache, where jwt hash is key, email is value
# Find user in db by email and set is_active status to false if no longer
# authenticated (i.e. logged out)
@router.post("/auth-context/")
async def check_auth_context():
    return JSONResponse(status_code=200, content={"message": "AOKay!"})
