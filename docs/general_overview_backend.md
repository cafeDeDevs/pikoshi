# General Overview - Backend

## Introduction

Pikoshi's backend codebase follows a traditional
[Model View Controller](https://en.wikipedia.org/w/index.php?title=Model%E2%80%93view%E2%80%93controller)(MVP)
Structure. Within the backend, one will find classic folder directories within
the `src/pikoshi` directory, where the majority of this document will reside
when introducing you to how Pikoshi is organized.

Please note that this document <em>only</em> gives a general overview of the
Backend of Pikoshi. Should you wish to read a General Overview of the Frontend,
please see [General Overview - Frontend](./general_overview_frontend.md).

Also note that Pikoshi's backend is built primarily using
[FastAPI](https://fastapi.tiangolo.com/), and thusly it is highly encouraged
that you take a look at the
[FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/) to get a high level
overview of the framework.

### The FastAPI Backend

As mentioned in the [Initial Setup](./initial_setup.md) documentation, Pikoshi
utilizes the [Rye](https://rye.astral.sh/) package manager. Pikoshi developers
utilize Rye to manage dependencies, act as a test runner, and also to manage
project related scripts. Rye utilizes the `backend/pyproject.toml` file as a
manifest for the Pikoshi Project. Of interest for understanding how Pikoshi
works is the custom `dev` script at the bottom of the `pyproject.toml` file:

```
[project.scripts]
dev = "pikoshi.main:main"
```

Thusly when we start the backend server:

```sh
rye run dev
```

We are calling whatever the `main()` function is within the
`src/pikoshi/main.py` file. If we inspect this file within our text editor, we
will find a layout that appears like so:

```py
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles

from .dependencies import get_db
from .meta import meta
from .middlewares import cors
from .routers import auth_context, gallery, google_auth, jwt_auth

app = FastAPI(**meta.meta_info, dependencies=[Depends(get_db)])

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
```

As you can see, the `main()` invocation utilizes the `uvicorn` package to start
our FastAPI server. This file provides a kind of configuration or manifest for
the rest of our FastAPI server. This file instantiates our main FastAPI server,
configures it with CORS middleware, mounts the `/public` folder so that the
server may serve static files. It also instantiates various routes, where a vast
majority of our API logic lives.

At the time of this writing (09/01/2024), Pikoshi has only just now begun the
final stages of establishing an Authentication Strategy involving both Google
OAuth2 and Email Authentication stratgies.

Thusly most of this document will attempt to demonstrate encouraged best
practices when writing and organizing your code when contributing to Pikoshi.
Let's begin by inspecting how our jwt_auth routes work.

### Routes

Within the `/routers` directory, one will find various router files named after
their purpose and/or role within the application. Let's get into the weeds a bit
and take a look at a subsection jwt_auth.py:

```py
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from jwt.exceptions import PyJWTError
from sqlalchemy.orm import Session

from ..config.redis_config import redis_instance as redis
from ..dependencies import get_db
from ..middlewares.logger import TimedRoute
from ..schemas.auth import TokenRequest
from ..schemas.user import UserInput, UserInputEmailPass, UserInputPass
from ..services.auth_service import AuthService
from ..services.email_service import EmailService
from ..services.exception_handler_service import ExceptionService
from ..services.jwt_service import JWTAuthService
from ..services.user_service import UserService
from ..utils.logger import logger

router = APIRouter(prefix="/auth", tags=["auth"], route_class=TimedRoute)


@router.post("/email-signup/")
async def signup_with_email(
    user_input: UserInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> Response:
    """
    - Grabs the user's email from the Client's /signup input form.
    - Checks to see if the user's email already exists within the DB.
    - If the user already exists, throw a 409 response back to the Client.
    - Otherwise Send a Transactional Email to the User using Resend,
      see EmailService.send_transac_email for details.
    - NOTE: send_transac_email sets hash token and user_email in redis cache.
    """
    try:
        user_email = user_input.email
        user_from_db = UserService.get_user_by_email(db, user_email)
        if user_from_db:
            raise HTTPException(
                status_code=409, detail="Email has already been registered."
            )

        await EmailService.send_transac_email(user_input, user_email, background_tasks)

        return JSONResponse(
            status_code=200, content={"message": "Email has been sent."}
        )
    except Exception as e:
        return ExceptionService.handle_generic_exception(e)
```

Like most Python files, we start off with importing whichever dependencies,
configurations, utils, and/or services we'll need. Of particular interest when
instantiating <em>new</em> routes is the use of the APIRouter instantiation:

```py
router = APIRouter(prefix="/auth", tags=["auth"], route_class=TimedRoute)
```

This router declaration is what is ultimately imported into our `main.py` file.
As you can see it establishes the prefix by which our other routes will be
prepended by. This router's prefix is `/auth`. If we follow this logic and take
a look at the instantiated route that follows it:

```py
@router.post("/email-signup/")
```

This means that the user can hit this route with an HTTP POST request by POSTing
to specifically this route:

```
localhost:8000/auth/email-signup/
```

As an aside, if you wish to see an OpenAPI documentation of all our routes,
FastAPI provides this sort of feature out of the box, simply visit:

```
localhost:8000/docs
```

And you will see the OpenAPI specs for all our routes (most at the time of this
writing require JWT authentication to utilize however).

Let's now move onto Schemas, and how they play a significant role in how FastAPI
ensures type safety using Pydantic Schemas:

### Schemas

```py
async def signup_with_email(
    user_input: UserInput,
    #...
```

This is the beginning of our example route above. As you can see, we define an
asynchronous route handler called `signup_with_email`, which takes an initial
parameter of `user_input`, which is then type defined as `UserInput`. Unlike
other Python backend frameworks, FastAPI utilizes Pydantic under the hood to
establisht hat should our `user_input` not follow the conventions of
`UserInput`, the route will actually fail to provide anything other than a
[422, Unprocessable Content](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/422)
reponse. This is because Pydantic is <em>enforcing that the fields provided in
`user_input` follow the conventions defined by our schemas</em>.

Let's follow the logic to understand what's exactly happening here. First and
foremost, where is this `UserInput` type coming from?:

```py
from ..schemas.user import UserInput, UserInputEmailPass, UserInputPass
```

Ah, there it is, we pull it in from two directories up (`..`), in the schemas
folder(`schemas`), in the user.py file (`.user`), and we import specifically the
declaration of the `UserInput` type. Let's take a look at that `schemas/user.py`
file:

```py
# TODO: Refactor these, too repetitive
# NOTE: Will require some thinking on the route handlers
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# ...
class UserInput(BaseModel):
    email: EmailStr
```

Pydantic models established from the BaseModel can be assumed to have nothing
more than a `body` field. From that though, we are then extending that
`BaseModel` class to include an `email` field, which will <em>only</em> accept a
string that follows the conventions followed by Pydantic's `EmailStr` class.

This means that when we hit this route:

```py
@router.post("/email-signup/")
async def signup_with_email(
    user_input: UserInput,
    #...
```

That the request object sent from the Client <em>must</em> have a `body` that
also has a `email` field, whose value must follow the conventions established by
Pydantic's `EmailStr` class.

Ultimately, FastAPI is <em>wrapping</em> the usual `request` object you see in
so many other Backend frameworks with a Pydantic Schema, which does the work of
ensuring the Client isn't passing us data that doesn't follow a certain
convention, strengthening the Type Safety of our application by not allowing the
User to passing input to our backend that does not follow the conventions we
established.

Note that there <em>is</em> a way to bypass Pydantic's schema validators via a
raw `request` object provided by FastAPI, but it is in my opinion not
recommended, as you would then need to validate input's manually within the
route handler instead.

There are also many other conventions followed using this kind of annotation.
For example, here is how one accesses the cookies appropriately from the request
object in FastAPI (on another one of our routes, `auth-context`):

```py
@router.post("/auth-context/")
async def check_auth_context(
    access_token: Annotated[str | None, Cookie()] = None,
    refresh_token: Annotated[str | None, Cookie()] = None,
    # ...
```

Or how uploaded files are handled:

```py
@router.post("/upload/")
async def upload_image_to_gallery(
    file: UploadFile,
    #...
```

FastAPI and Pydantic provide a powerful set of checks and balances by utilizing
the type checking provided by Pydantic schemas to ensure that routes are only
passed data with keys and values that we as developers <em>intended</em> to be
present!

**A Word On Code Organization/Style:**

Our routes condense the various logic needed to create the desired output when
the Client queries a backend route. Thusly it is encouraged that you organize
your code into configurations, utils, and most importantly, <em>services</em>
when implementing the logic for a backend route.

<b><em>Ideally backend routes should not have a lot of code</em></b>. Initially,
when first fleshing out the logic related to a Ticket you receive, you should
feel free to put all your logic into the route, but once you find yourself
saying "This route does this, and then this, and then this, and then also
this...", it's time to start abstracting out the code into multiple subroutines,
also known as <em>helper functions</em>.

You can initially keep these helper functions within the route file as well, but
eventually you'll want to put them into a "service" file. Whether you put these
helper functions into an existing "service" file or a new one is up to you, but
you should try to follow the conventions established by the Project Lead and
encapsulate your services into a Class. If you find you only need a one off
helper function (in which you may use it often, but is unrelated to any other
service), consider putting these helper functions into a `/utils` file.

On this note, let's take a look at one of our services within our
`signup_with_email` route example from earlier:

### Services

```py
user_from_db = UserService.get_user_by_email(db, user_email)
```

You'll find this line pretty early on in the `signup_with_email` route handler
logic. The semantics are meant to give you an inclination of what is happening
under the hood. As mentioned earlier in the <b>Code Organization/Style</b>
section, you can first flesh out your logic within the route handler file
itself, but as soon as you find yourself feeling a little lost as to "what
exactly is going on?" and feel the need to create a bunch of comments to
explain, it's probably best to create a helper function with a descriptive name
that does what your comment is trying to explain.

Helper functions generally should do only <em>one</em> thing. Thusly it is
<em>perfectly fine</em> to have multiple helper functions within your routes, as
long as the naming of said functions is relatively clear. Helper functions
should also be grouped into Service Classes, which generalize the main entity
that the helper functions interact with. In this case this class `UserService`
is implied to deal with functions related to interacting with the `User`.
Specifically, this `UserService` deals with logic mainly in the realm of
interacting with the `User` table in the Database. Let's take a closer look at
our UserService Class. First and foremost though, where is it coming from?:

```py
from ..services.user_service import UserService
```

Ah okay, it's imported from two directories up (`..`), in the services directory
(`services`) in the `user_service.py` file (`user_service`). And we import in an
entire `UserService` class. Let's take a look at that file and class:

```py
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from ..models.user import User as UserModel
from ..schemas.user import User, UserCreate


class UserService:
    #...
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        """
        - Grabs the User by Email.
        """
        return db.query(UserModel).filter(UserModel.email == email).first()
    #...
```

Ah, okay, now we're getting somewhere, we use the SQLAlchemy `db` instance
established by the route handler, and then use it to query the `User` table,
here brought in as a SQLAlchemy `UserModel` so as to avoid confusion with the
Pydantic `User` schema. We pass the SQLAlchemy ORM the email string, and use it
to query the `User` table, looking for a User with that email string. Once we
find it, we simply return the first instance of User.

**Wait, where did this `db` instance come from?:**

Yeah, we didn't exactly cover that, did we? Let's backtrack to where this gets
passed, within our route handler:

```py
@router.post("/email-signup/")
async def signup_with_email(
    user_input: UserInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    #...
```

This is a convention established in FastAPI's beginner tutorial series.
Essentially Here in the Route handler we establish an SQLAlchemy Session, which
is brought in here:

```py
from sqlalchemy.orm import Session
```

We then tell FastAPI, that this SQLAlchemy `Depends` on the `get_db` dependency:

```py
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
#...
from ..dependencies import get_db
```

You can take a look at this `get_db` dependency directly at the
`/src/pikoshi/dependencies.py` file:

```py
from .database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Which establishes a local SQLAlchemy instance. Let's take a look at this
`SessionLocal` while we're at it (in `/src/pikoshi/database.py`):

```py
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
PG_HOST = os.environ.get("PG_HOST") or "localhost"
PG_PORT = int(str(os.environ.get("PG_PORT"))) or 5432
PG_USER = os.environ.get("PG_USER") or "admin"
PG_PASS = os.environ.get("PG_PASS") or "postgres"
PG_DB = os.environ.get("PG_DB") or "phlint_db"

# PostgreSQL Configuration
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"
)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

Ah... lots of magic here. Nevertheless, for our purposes we are establishing a
connection to our PostgreSQL database, and are able to interact with it via
SQLAlchemy Models...wait, so what about that User model brought in earlier?

### Database Models With SQLAlchemy

SQLAlchemy provides a commonly used convention known as a Database Model. This
is interacted with via a Class Instantiation that is utilized to establish the
various Columns within our database tables. We can see the instantiation of our
SQLAlchemy User Model in the `/src/pikoshi/models/user.py` file:

```py
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String(30), unique=False, index=True)
    password = Column(String(254), nullable=False, index=True)
    salt = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(Text, unique=True, index=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, nullable=True, default=False)
    last_login = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(name='{self.name}', email='{self.email}', is_active={self.is_active})>"
```

Database Models are a common convention whenever working with Database ORMs, and
SQLAlchemy is no different. If we wish to have a new Column/Field within our
database to interact with data, we first have to instantiate it here.

But if we were to add this to our Model, how can we be sure that our Database is
updated to have these fields? How do we <em>migrate</em> our changes? Well,
that's where Alembic comes into play.

### Database Migrations With Alembic

For the sake of an example, let's say that I needed to add a new Column/Field to
my `user` table, let's say I wanted a `is_not_active` boolean field that simply
showed if the `user` did not have an active authentication session on Pikoshi.
We could adjust our above model pretty simply like so:

```py
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String(30), unique=False, index=True)
    password = Column(String(254), nullable=False, index=True)
    salt = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(Text, unique=True, index=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, nullable=True, default=False)
    is_not_active = Column(Boolean, nullable=True, default=True) # ** OUR NEW COLUMN **
    last_login = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(name='{self.name}', email='{self.email}', is_active={self.is_active})>"
```

But our DB would need to be repopulated...this is where migrations come in.
Database migrations one can think of as a kind of source control for our
Database. We could create many migrations that could keep track of the various
changes to our database structure (adding new columns, deleting old columns,
adding new tables, removing old tables, etc.). At the time of this writing
(09/01/2024), Pikoshi is in a very simple state, and thusly only has one
migration file to worry about. So how do we get this new `is_not_active` field
into our Database using Alembic migrations?

Well, first let's edit our migration file. You can find it in
`src/pikoshi/migrations/versions`. Here you'll find a migration file with a long
version number string prepended to the title of the migration
`added_users_table.py`. Let's take a look at this file:

```py
"""Added users table

Revision ID: 25b556f883b8
Revises:
Create Date: 2024-08-22 04:19:34.619552

"""

from os import walk
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "25b556f883b8"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("created", sa.DateTime(timezone=True)),
        sa.Column("name", sa.String(length=30), unique=False, index=True),
        sa.Column("password", sa.String(length=254), nullable=False, index=True),
        sa.Column("salt", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("email", sa.Text, unique=True, index=True),
        sa.Column("uuid", sa.String(36), unique=True, nullable=False, index=True),
        sa.Column("is_active", sa.Boolean(), default=False),
        sa.Column("last_login", sa.DateTime(timezone=True)),
    )
    #...
```

Ah, okay, so very similar to our SQLAlchemy Model instantiation. In fact, we can
almost copy the same new `is_not_active` field over here. Let's add it to our
migration file:

```py
def upgrade() -> None:
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("created", sa.DateTime(timezone=True)),
        sa.Column("name", sa.String(length=30), unique=False, index=True),
        sa.Column("password", sa.String(length=254), nullable=False, index=True),
        sa.Column("salt", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("email", sa.Text, unique=True, index=True),
        sa.Column("uuid", sa.String(36), unique=True, nullable=False, index=True),
        sa.Column("is_active", sa.Boolean(), default=False),
        sa.Column("is_not_active", sa.Boolean(), default=True),
        sa.Column("last_login", sa.DateTime(timezone=True)),
    )
    #...
```

Okay, so we've edited both our migration file and our models file. Now how do we
actually update the `users` table?

To do that, we'll need to ensure we are inside our Python virtual environment.
From within our `/backend` directory:

```sh
source .venv/bin/activate
```

And once inside our virtual environment, navigate into the `src/pikoshi` folder:

```sh
cd src/pikoshi
```

From here, we can now invoke `alembic` to first downgrade our tables:

```sh
alembic downgrade -1
```

This will downgrade our last change and drop all our tables (you can see the
logic for this in the migration script file we were just editing towards the
bottom). Now let's bring in our new changes and populate our DB with our update
`users` table:

```sh
alembic upgrade head
```

And that's it! You should now have an upgraded `users` table with a new
`is_not_active` field.

### Testing

:construction: NOTE: This section is very incomplete.

The Rye package manager also acts as a test runner. In particular, Pikoshi unit
tests utilize the [PyTest](https://docs.pytest.org/en/stable/) testing suite to
test it's application. At the time of this writing (09/01/2024), Pikoshi only
has a single Sample Unit Test that utilizes an in memory SQLite database to
mimic calls to the Database. Once more tests are written, this section of the
<b>General Overview - Backend</b> will be revisited.

That said, should you wish to run the test runner (which will probably fail at
the time of this writing), you can do so using `rye`:

```sh
rye test
```

## Conclusion

Obviously, there is <em>a lot</em> going on here. FastAPI does have a lot of
power under the hood, but it doesn't provide you with an "Out Of The Box"
experience like Meta Frameworks such as Django or Laravel do. However, this
makes FastAPI extremely customizable, and hopefully I have established a
straight forward enough directory structure, series of established coding best
practices, and insights here for you to get started making your own
routes/services as well as schemas/models for you to contribute effectively to
Pikoshi and potentially utilizing this backend stack in your own projects!
