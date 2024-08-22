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

# SQLite Configuration
# SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
# engine = create_engine(
# SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
# NOTE: Importation of DB models must occur AFTER declaration of Base.
# NOTE: No longer necessary after using alembic migrations
#  from .models.item import Item
#  from .models.user import User

#  Base.metadata.create_all(bind=engine)
