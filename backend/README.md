# Pikoshi (Backend)

Pikoshi: The Photo Sharing Application With Privacy In Mind By Default 🐱

## Introduction

This directory contains the backend for the application, Pikoshi.

**PreRequisite Dependencies:**

Before diving into Pikoshi's codebase, you'll first need to have
[python](https://www.python.org/downloads/),
[docker](https://docs.docker.com/engine/install/), and
[rye](https://rye.astral.sh/guide/installation/) installed.

**Getting Started:**

Once those are installed, you'll also need to simply copy the included
`env-sample` file as a `.env` to adjust from the default `HOST` and `PORT`:

```sh
cp env-sample .env
```

Once cloned and inside the project's directory. go ahead and use rye to initiate
the virtual environment (defaults to a `.venv` directory):

```sh
rye sync
```

This will also install all necessary dependencies needed. After that, you'll
need to instantiate your virtual environment like so:

```sh
source .venv/bin/activate
```

You'll need to migrate the database so that the essential tables are
established. You can do this with alembic:

```sh
alembic upgrade head
```

After you've migrated the database, you can then run the server itself using the
`dev` script:

```sh
rye run dev
```

The default port utilized for this template is 8000. So once you see the
fastapi-cli's output, indicating successful startup of the server, you can
simply navigate in your browser to localhost:8000/docs to see the OpenAPI
documentation of the app.

### About The App

This App is just a template, but can be utilized as a model on how to organize
future applications/projects.

**The Rye Package Manager**

This project utilizes the modern python project/package manager
[Rye](https://rye.astral.sh/). Please see their
[Installation Instructions](https://rye.astral.sh/guide/installation/) if you
don't have it installed.

While the official [User Guide](https://rye.astral.sh/guide/) should provide you
with all the information you'll need to get started using Rye, Here are a few
common commands you might find yourself needing to use throughout building your
application

```sh
# Adding a package
rye add package_name
# Removing a package
rye remove package_name
# Adding a dev dependency
rye add --dev package_name
# Removing a dev dependency
rye remove --dev package_name
# Syncing Your Project With The Virtual Environment
# (run after installing/uninstalling dependencies)
rye sync
```

Should you find yourself ready to build/publish your application, please consult
Rye's Official Documentation on
[Building and Publishing](https://rye.astral.sh/guide/publish/).

**SQLAlchemy And Setting Up The Database**

This App template uses the [SQLAlchemy ORM](https://www.sqlalchemy.org/), and
thusly can utilize any of the classic SQL databases including [SQLite](),
[Postgresql](https://www.postgresql.org/), [MySQL](https://www.mysql.com/) &
[MariaDB](https://mariadb.org/),
[Oracle](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Introduction-to-Oracle-SQL.html),
and [MS-SQL](https://www.microsoft.com/en-us/sql-server/sql-server-downloads).

**Instantiating PostgreSQL Via Docker**

This version of the App template gives you the option of utilizing either SQLite
or PostgreSQL databases (and uses an in memory SQLite DB in testing). Depending
on which DB you want to use, you'll need to adjust a few settings. By default,
the App uses a PostgreSQL database within a [Docker](https://www.docker.com/)
container (setup using [docker compose](https://docs.docker.com/compose/)).

To initialize the database, you simply have to fill out the appropriate Database
URI fields within your `.env` file:

```
# Postgres Config
PG_HOST="127.0.0.1"
PG_PORT=5936
DB_PORT=5432
PG_USER="admin"
PG_DB="app_db"
PG_CONTAINER_NAME="app_db"
PG_PASS="postgres"
```

If you are just working in development and have port 5936 available on your
development machine, you can leave these fields the same (but I advise that
should you push your application to production that you adjust these default
settings).

Once your `.env` variables are set up, you can use `docker compose` to
instantiate your docker images/containers:

```sh
docker compose -f ./docker-compose.yml up -d
```

You can check the status of your docker containers to ensure they are running
like so:

```sh
docker container ls -a
```

Once you are sure your docker containers are running you can then use
[Alembic](https://alembic.sqlalchemy.org/en/latest/) to migrate your initial
tables into the database.

**Using SQLite Instead**

Should you wish to use the more straight forward database, SQLite, you can
forego the previous docker related section. You will need to change three
configuration fields in order to get it working however.

Firstly, we'll have to change our FastAPI server's configuration to look at a
different Database URI. This can be done within our src/pikoshi/database.py
file. Firstly, comment out all the PostgreSQL configurations:

```py
# database.py
# PostgreSQL Configuration
# SQLALCHEMY_DATABASE_URL = (
#     f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"
# )
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
```

And then uncomment the SQLite Configuration:

```py
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
```

Next you'll need to uncomment the `sqlalchemy.url` in the `alembic.ini` file
(located at the root of the project directory):

```ini
# SQLite Configuration
sqlalchemy.url = sqlite:///./app.db
```

And lastly, you'll need to comment out the `config.set_main_option()`
configuration in the `migrations/env.py` file:

```py
# PostgreSQL Configuration
# config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)
```

Once these configuration settings have been adjusted, you can then use
[Alembic](https://alembic.sqlalchemy.org/en/latest/) to migrate your initial
tables into the database.

**Using Alembic To Set Up Your Initial Tables**

You can initialize your first database migration by first invoking `alembic`
with the `upgrade head` command:

```sh
alembic upgrade head
```

Should you need to downgrade the migration (roll back your previous changes to
the database), you can simply invoke `alembic` with the `downgrade -1`
command/flag:

```sh
alembic downgrade -1
```

Which will downgrade alembic by exactly 1 migration (you can further revert back
your changes to the database by indicationg numerically how many you'd like to
go back). You can find all migration scripts within the `migrations` directory
within the root of the projec directory located at the root of the project.

Should you need to add new tables you can generate a new migration script:

```sh
alembic revision --autogenerate -m "Added users table"
```

**Static Files**

FastAPI provides for use of static files very easily. To serve static files,
place them in the `src/pikoshi/public` folder. The server is set up to serve any
static files placed here by default. To view them in your browser, simply enter
the url
<em>localhost:8000/public/<b>name_of_your_file.jpg</b></em> and you should see
your file displayed there.

Provided with this template is a sample jpeg of the FastAPI Logo you can view
from your browser while the server is running. Simply visit
<em>localhost:8000/public/fastapi-logo.png</em>

Should you wish to know more about static files in FastAPI, please see their
[tutorial on the subject](https://fastapi.tiangolo.com/tutorial/static-files/).

**Testing**

FastAPI favors using [pytest](https://docs.pytest.org/en/stable/) to run unit
tests for FastAPI applicactions. If you wish to run the tests, don't utilize
`pytest` directly. Instead, simply invoke `rye test` to run them (uses `pytest`
under the hood, do <em>not</em> invoke `pytest` directly as that will error out
when trying to import dependencies):

```sh
rye test
```

**Editor Tooling**

This project utilizes some additional editor tooling for use with python. These
include:

- [black (code formatter)](https://black.readthedocs.io/en/stable/index.html)
- [isort (dependency organizer)](https://pycqa.github.io/isort/)
- [pyright (python linter)](https://github.com/microsoft/pyright)

You can install the [VSCode](https://code.visualstudio.com/) extensions via your
editor or you can download them directly from the
[Visual Studio Marketplace](https://marketplace.visualstudio.com/):

- [VSCode black](https://marketplace.visualstudio.com/items?itemName=mikoz.black-py)
- [VSCode isort](https://marketplace.visualstudio.com/items?itemName=ms-python.isort)
- [VSCode pyright](https://marketplace.visualstudio.com/items?itemName=ms-pyright.pyright)

Additionally, the Neovim equivalents can be downloaded directly, downloaded
using a extensions tool like
[Mason](https://github.com/williamboman/mason.nvim):

- [NeoVim black](https://github.com/averms/black-nvim)
- [NeoVim isort](https://github.com/stsewd/isort.nvim)
- [NeoVim pyright](https://www.andersevenrud.net/neovim.github.io/lsp/configurations/pyright/)

I personally use [NeoVim](https://neovim.io/) and an all in one formatter,
[conform](https://github.com/stevearc/conform.nvim). I did, however, download
pyright using Mason.

## Conclusion

This is the most organized workflow I've found using FastAPI (or any Python
project for that matter). There are more features I plan on adding to this
template like working with
[OAuth2 and JWT tokens](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/).
This repository is mainly meant for my own personal use for scaffolding off of
into future projects, but perhaps you, dear reader, might also find it useful.
