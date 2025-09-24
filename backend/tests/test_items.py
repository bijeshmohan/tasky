from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from api.common import Status, Priority, Type
from api.schemas.item import ItemRead


@pytest.fixture
def credentials(client: TestClient):
    data = {"username": "alice", "password": "secret"}

    r = client.post(
        "/users",
        json=data
    )
    assert r.status_code == 201
    return data


@pytest.fixture
def token(client: TestClient, credentials: dict):
    r = client.post(
        "/auth/token",
        data={
            "username": credentials["username"],
            "password": credentials["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, r.text
    t = r.json()["token"]
    assert t and isinstance(t, str)
    return t


@pytest.fixture
def header(token: str):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def item(client: TestClient, header: dict):
    r = client.post("/items", json={"summary": "lorem ipsum"}, headers=header)
    if r.status_code != 201:
        raise RuntimeError("Unable to create Item!")
    return r.json()


@pytest.fixture
def items(client: TestClient, header: dict):
    items = []
    for i in range(5):
        r = client.post("/items", json={"summary": f"lorem ipsum {i}"}, headers=header)
        if r.status_code != 201:
            raise RuntimeError("Unable to create Item!")
        items.append(r.json())
    return items


def test_create_item_with_mandatory_fields(client: TestClient, header: dict):
    summary = "lorem ipsum"
    r = client.post("/items", json={"summary": summary}, headers=header)
    assert r.status_code == 201
    validated = ItemRead(**r.json())
    assert validated.summary == summary
    assert validated.description is None
    assert validated.type == Type.TASK
    assert validated.priority == Priority.MEDIUM
    assert validated.due is None
    assert validated.status == Status.TODO


def test_create_item_with_optional_fields(client: TestClient, header: dict):
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
        },
        headers=header
    )
    assert r.status_code == 201
    validated = ItemRead(**r.json())
    assert validated.summary == summary
    assert validated.description == description
    assert validated.type == Type.BUG
    assert validated.priority == Priority.HIGH
    assert validated.due == datetime.fromisoformat(due)
    assert validated.status == Status.TODO


def test_read_item(client: TestClient, item: dict, header: dict):
    r = client.get(f"/items/{item['id']}", headers=header)
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


def test_read_unavailable_item(client: TestClient, header: dict):
    id = uuid4()
    r = client.get(f"/items/{id}", headers=header)
    assert r.status_code == 404
    data = r.json()
    assert data["detail"] == f"Work Item {id} NOT FOUND!"


def test_read_items(client: TestClient, items: list[dict], header: dict):
    r = client.get("/items", headers=header)
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


def test_update_item(client: TestClient, item: dict, header: dict):
    update = "foo bar"
    r = client.patch(
        f"/items/{item['id']}",
        json={"summary": update},
        headers=header
    )
    assert r.status_code == 200
    validated = ItemRead(**r.json())
    assert validated.summary == update
    # TODO: validate other fields remain unchanged


def test_update_unavailable_item(client: TestClient, header: dict):
    id = uuid4()
    r = client.patch(
        f"/items/{id}",
        json={"summary": "foo bar"},
        headers=header
    )
    assert r.status_code == 404
    data = r.json()
    assert data["detail"] == f"Work Item {id} NOT FOUND!"


def test_delete_item(client: TestClient, item: dict, header: dict):
    r = client.delete(f"/items/{item['id']}", headers=header)
    assert r.status_code == 204


def test_delete_unavailable_item(client: TestClient, header: dict):
    id = uuid4()
    r = client.delete(f"/items/{id}", headers=header)
    assert r.status_code == 404
    data = r.json()
    assert data["detail"] == f"Work Item {id} NOT FOUND!"
