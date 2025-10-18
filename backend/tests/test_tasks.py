from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from backend.common import Priority
from backend.schemas.task import TaskRead


@pytest.fixture
def endpoint():
    return "/tasks"


@pytest.fixture
def credentials(client: TestClient):
    data = {"username": "alice", "password": "p@55W0rd"}

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
def task(client: TestClient, endpoint: str, header: dict):
    r = client.post(endpoint, json={"summary": "lorem ipsum"}, headers=header)
    if r.status_code != 201:
        raise RuntimeError("Unable to create Task!")
    return r.json()


@pytest.fixture
def tasks(client: TestClient, endpoint: str, header: dict):
    tasks = []
    for i in range(5):
        r = client.post(endpoint, json={"summary": f"lorem ipsum {i}"}, headers=header)
        if r.status_code != 201:
            raise RuntimeError("Unable to create Task!")
        tasks.append(r.json())
    return tasks


def test_create_task_with_mandatory_fields(client: TestClient, endpoint: str, header: dict):
    summary = "lorem ipsum"
    r = client.post(endpoint, json={"summary": summary}, headers=header)
    assert r.status_code == 201
    validated = TaskRead(**r.json())
    assert validated.summary == summary
    assert validated.description is None
    assert validated.priority == Priority.MEDIUM
    assert validated.due is None
    assert validated.done == False


def test_create_task_with_optional_fields(client: TestClient, endpoint: str, header: dict):
    summary = "lorem ipsum"
    description = "The quick brown fox jumps over the lazy dog"
    priority = 1
    due = (datetime.now() + timedelta(days=7)).isoformat()
    r = client.post(
        endpoint,
        json={
            "summary": summary,
            "description": description,
            "priority": priority,
            "due": due
        },
        headers=header
    )
    assert r.status_code == 201
    validated = TaskRead(**r.json())
    assert validated.summary == summary
    assert validated.description == description
    assert validated.priority == Priority.HIGH
    assert validated.due == datetime.fromisoformat(due)
    assert validated.done == False


def test_read_task(client: TestClient, endpoint: str, task: dict, header: dict):
    r = client.get(f"{endpoint}/{task['uuid']}", headers=header)
    assert r.status_code == 200
    validated = TaskRead(**r.json())
    assert validated.uuid == UUID(task["uuid"])
    assert validated.summary == task["summary"]
    assert validated.description == task["description"]
    assert validated.priority == Priority(task["priority"])
    assert validated.due == (datetime.fromisoformat(task["due"]) if task["due"] else None)
    assert validated.done == task["done"]
    assert validated.created == datetime.fromisoformat(task["created"])


def test_read_unavailable_task(client: TestClient, endpoint: str, header: dict):
    uuid = uuid4()
    r = client.get(f"{endpoint}/{uuid}", headers=header)
    assert r.status_code == 404
    data = r.json()
    assert data["detail"] == f"Task {uuid} NOT FOUND!"


def test_read_tasks(client: TestClient, endpoint: str, tasks: list[dict], header: dict):
    r = client.get(endpoint, headers=header)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == len(tasks)
    for task in data:
        validated = TaskRead(**task)
        assert validated.uuid == UUID(task["uuid"])
        assert validated.summary == task["summary"]
        assert validated.description == task["description"]
        assert validated.priority == Priority(task["priority"])
        assert validated.due == (datetime.fromisoformat(task["due"]) if task["due"] else None)
        assert validated.done == task["done"]
        assert validated.created == datetime.fromisoformat(task["created"])


def test_update_task(client: TestClient, endpoint: str, task: dict, header: dict):
    update = "foo bar"
    r = client.patch(
        f"{endpoint}/{task['uuid']}",
        json={"summary": update},
        headers=header
    )
    assert r.status_code == 200
    validated = TaskRead(**r.json())
    assert validated.summary == update
    # TODO: validate other fields remain unchanged


def test_update_unavailable_task(client: TestClient, endpoint: str, header: dict):
    id = uuid4()
    r = client.patch(
        f"{endpoint}/{id}",
        json={"summary": "foo bar"},
        headers=header
    )
    assert r.status_code == 404
    data = r.json()
    assert data["detail"] == f"Task {id} NOT FOUND!"


def test_delete_task(client: TestClient, endpoint: str, task: dict, header: dict):
    r = client.delete(f"{endpoint}/{task['uuid']}", headers=header)
    assert r.status_code == 204


def test_delete_unavailable_task(client: TestClient, endpoint: str, header: dict):
    uuid = uuid4()
    r = client.delete(f"{endpoint}/{uuid}", headers=header)
    assert r.status_code == 404
    data = r.json()
    assert data["detail"] == f"Task {uuid} NOT FOUND!"
