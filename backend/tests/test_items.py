from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from api.common import Status, Priority, Type
from api.main import app, get_session
from api.schemas import ItemRead


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


@pytest.fixture
def client(session: Session):
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    c = TestClient(app)
    yield c
    app.dependency_overrides.clear()


@pytest.fixture
def item(client: TestClient):
    r = client.post("/items", json={"summary": "lorem ipsum"})
    if r.status_code != 201:
        raise RuntimeError("Unable to create Item!")
    return r.json()


@pytest.fixture
def items(client: TestClient):
    items = []
    for i in range(5):
        r = client.post("/items", json={"summary": f"lorem ipsum {i}"})
        if r.status_code != 201:
            raise RuntimeError("Unable to create Item!")
        items.append(r.json())
    return items


def test_create_item_with_mandatory_fields(client: TestClient):
    summary = "lorem ipsum"
    r = client.post("/items", json={"summary": summary})
    assert r.status_code == 201
    validated = ItemRead(**r.json())
    assert validated.summary == summary
    assert validated.description is None
    assert validated.type == Type.TASK
    assert validated.priority == Priority.MEDIUM
    assert validated.due is None
    assert validated.status == Status.TODO


def test_create_item_with_optional_fields(client: TestClient):
    summary = "lorem ipsum"
    description = "The quick brown fox jumps over the lazy dog"
    type = "bug"
    priority = 1
    due = (datetime.now() + timedelta(days=7)).isoformat()
    r = client.post(
        "/items",
        json={
            "summary": summary,
            "description": description,
            "type": type,
            "priority": priority,
            "due": due
        }
    )
    assert r.status_code == 201
    validated = ItemRead(**r.json())
    assert validated.summary == summary
    assert validated.description == description
    assert validated.type == Type.BUG
    assert validated.priority == Priority.HIGH
    assert validated.due == datetime.fromisoformat(due)
    assert validated.status == Status.TODO


def test_read_item(client: TestClient, item: dict):
    r = client.get(f"/items/{item['id']}")
    assert r.status_code == 200
    validated = ItemRead(**r.json())
    assert validated.id == UUID(item["id"])
    assert validated.summary == item["summary"]
    assert validated.description == item["description"]
    assert validated.type == Type(item["type"])
    assert validated.priority == Priority(item["priority"])
    assert validated.due == (datetime.fromisoformat(item["due"]) if item["due"] else None)
    assert validated.status == Status(item["status"])
    assert validated.created == datetime.fromisoformat(item["created"])


def test_read_unavailable_item(client: TestClient):
    id = uuid4()
    r = client.get(f"/items/{id}")
    assert r.status_code == 404
    data = r.json()
    assert data["detail"] == f"Work Item {id} NOT FOUND!"


def test_read_items(client: TestClient, items: list[dict]):
    r = client.get("/items")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == len(items)
    for item in data:
        validated = ItemRead(**item)
        assert validated.id == UUID(item["id"])
        assert validated.summary == item["summary"]
        assert validated.description == item["description"]
        assert validated.type == Type(item["type"])
        assert validated.priority == Priority(item["priority"])
        assert validated.due == (datetime.fromisoformat(item["due"]) if item["due"] else None)
        assert validated.status == Status(item["status"])
        assert validated.created == datetime.fromisoformat(item["created"])


def test_update_item(client: TestClient, item: dict):
    update = "foo bar"
    r = client.patch(f"/items/{item['id']}", json={"summary": update})
    assert r.status_code == 200
    validated = ItemRead(**r.json())
    assert validated.summary == update
    # TODO: validate other fields remain unchanged


def test_update_unavailable_item(client: TestClient):
    id = uuid4()
    r = client.patch(f"/items/{id}", json={"summary": "foo bar"})
    assert r.status_code == 404
    data = r.json()
    assert data["detail"] == f"Work Item {id} NOT FOUND!"


def test_delete_item(client: TestClient, item: dict):
    r = client.delete(f"/items/{item['id']}")
    assert r.status_code == 204


def test_delete_unavailable_item(client: TestClient):
    id = uuid4()
    r = client.delete(f"/items/{id}")
    assert r.status_code == 404
    data = r.json()
    assert data["detail"] == f"Work Item {id} NOT FOUND!"
