import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles

from .database import sessionmanager
from .dependencies import get_db_session
from .meta import meta
from .middlewares import cors
from .routers import auth_context, gallery, google_auth, jwt_auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read:
    https://fastapi.tiangolo.com/advanced/events/
    """
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


app = FastAPI(
    lifespan=lifespan, **meta.meta_info, dependencies=[Depends(get_db_session)]
)

cors.add_cors_middleware(app)

app.mount("/public", StaticFiles(directory="src/pikoshi/public"), name="static")

load_dotenv()
HOST = os.environ.get("HOST") or "::"
PORT = int(str(os.environ.get("PORT"))) or 8000

app.include_router(google_auth.router)
app.include_router(jwt_auth.router)
app.include_router(auth_context.router)
app.include_router(gallery.router)


def main():
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
