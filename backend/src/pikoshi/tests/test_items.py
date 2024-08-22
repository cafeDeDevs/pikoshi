from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..database import SQLALCHEMY_DATABASE_URL, Base
from ..dependencies import get_db
from ..main import app
from ..models.item import Item

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)


def test_get_items_empty() -> None:
    response = client.get("/items/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_items_with_data() -> None:
    test_item = Item(title="Test Item", description="This is a test item", owner_id=1)
    db = TestingSessionLocal()
    db.add(test_item)
    db.commit()
    db.refresh(test_item)

    response = client.get("/items/")
    assert response.status_code == 200
    items = response.json()

    assert len(items) == 1
    assert items[0]["title"] == "Test Item"
    assert items[0]["description"] == "This is a test item"
