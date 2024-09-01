# Initial Setup

## Introduction

Once you have cloned and navigated into the repository's main directory per the
instructions in Pikoshi's main [README](../README.md), you can begin to process
of installing the needed dependencies, both global and local, instantiating the
needed docker containers, as well as filling in the needed environment variables
for use within the development of the application.

### Global Dependencies

You'll need a few things installed on your machine before getting started.
Pikoshi utilizes Python3 and NodeJS on the backend and frontend respectively, so
you'll need to ensure those are installed:

- [Install Python3](https://www.python.org/downloads/)
- [Install NodeJS](https://nodejs.org/en/learn/getting-started/how-to-install-nodejs)

You will also need Docker installed:

- [Install Docker](https://docs.docker.com/engine/install/)

Pikoshi also utilizes very modern package managers on both the backend and
frontend. For the backend, you'll need to install the Rye Package manager:

- [Install Rye](https://rye.astral.sh/guide/installation/)

And on the frontend, we use bun instead of npm, so please install bun as well:

- [Install Bun](https://bun.sh/docs/installation)

Once those package managers are installed, that'll be it for global
dependencies. Next let set up your local dependencies.

### Local Dependencies

**Backend:**

From within the project's root directory (same directory as the README.md),
navigate first to the backend:

```sh
cd backend
```

From here we're going to use `rye` to install all the necessary packages and
also instantiate a Python virtual environment:

```sh
rye sync
```

You should see some output indicating the installation of the needed packages.
You can also list out all hidden files to see that the virutal environment
directory `./venv` was installed:

```sh
ls -a
```

You can also simply invoke the virtual environment using `source`:

```sh
source .venv/bin/activate
```

Your shell should give you some sort of output indicating you are now in a
virtual environment. As long as the dependencies are installed and the virutal
environment is instantiated, your dependencies are all set. Let's move onto the
frontend.

**Frontend:**

Navigate from the backend directory into the frontend:

```sh
cd ../frontend
```

From here you can now use `bun` to install the needed local dependencies:

```sh
bun install
```

You should see some output indicating that the dependencies have been installed.
Now we can move onto establishing the environment variables.

### Environment Variables

The Project Lead should have sent you the needed environment variables during
onboarding. Within both the `frontend` and `backend` directories, you should
find an `env-sample` file. Copy this file into a new file called `.env`:

```sh
cp env-sample .env
```

Now fill in the respective fields that are currently empty (i.e. no fields are
provided after the "=" character) using the file provided by your Project Lead,
the names within the provided `frontend_secrets.txt` file should correspond so
it's relatively straight forward to figure out which fields go where.

Similarly, do the same on the backend. Navigate to the backend:

```sh
cd ../backend
```

And copy the `env-sample` file to a new `.env` file:

```sh
cp env-sample .env
```

And fill in the appropriate fields from the `backend_secrets.txt` file provided
from the Project Lead.

### Instantiating Docker Containers

Pikoshi relies on Dockerized versions of both a PosgreSQL database and a Redis
cache. Luckily, it's not too difficult to set up these containers from the
command line. Within the `/backend` directory, simply invoke the
`docker compose` command like so:

```sh
docker compose -f ./docker-compose.yml up -d
```

You should see some output as docker pulls in the required docker images and
then instantiates the docker containers. To verify that the docker containers
are up and running invoke:

```sh
docker container ls
```

You should see a table like output. Of importance is to note the `STATUS` field,
where below you should see whether both docker containers are up and running.
Note that if you had any problems with this setup, make sure to check that there
are no applications running on ports 5936 and 6380, as these ports are needed to
instantiate these containers.

Now that you have instantiated the database, we'll need to populate it with the
initial tables. Pikoshi utilizes the migration tool,
[Alembic](https://alembic.sqlalchemy.org/en/latest/) to populate it's database
and handle it's migrations.

### Migrating Initial Tables

Within the `/backend` directory, make sure you have instantiated the virtual
environment:

```sh
source .venv/bin/activate
```

After that, navigate into the `/src/pikoshi` directory:

```sh
cd src/pikoshi
```

From within this directory, you can migrate the initial tables using `alembic`:

```sh
alembic upgrade head
```

This will set up the initial SQL tables. You should see a small amount of output
indicating the population of the tables.

### Starting The Application

Once all the aforementioned is done, you now can start the application. You'll
need to open two terminal windows and navigate one to the backend, and the other
to the frontend.

**Starting the Backend:**

On the backend terminal, once in the `/backend` directory, instantiate your
virtual environment like so:

```sh
source .venv/bin/activate
```

And then use `rye` to start the development server:

```sh
rye run dev
```

You should see some output indicating the startup of the backend server.

**Starting the Frontend:**

In the other terminal window in which you have navigated to the `/frontend`
directory, you can simply start the server using `bun`:

```sh
bun dev
```

You should see some output indicating the start up of the frontend server. You
can verify everything is working by navigating in your browser to:

```
localhost:5173
```

Here you will be presented with Pikoshi's splash screen and a link to login. The
sign up process at the time of this writing is more or less complete, so feel
free to sign up via Google or Email to create an account on your local instance
of Pikoshi. You are now ready to start development!

Please refer to the [General Overview - Backend](./general_overview_backend.md)
document to get a general introduction to the backend codebase. Similarly,
please refer to [General Overview - Frontend](./general_overview_frontend.md) to
get a general introduction to the frontend codebase.

Please also refer to our documents on [Tooling](./tooling.md) for a list of
developer tools that are required in order to contribute to Pikoshi.
