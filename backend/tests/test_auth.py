import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def credentials(client: TestClient):
    data = {"username": "alice", "password": "p@55W0rd"}

    r = client.post(
        "/users",
        json=data
    )
    assert r.status_code == 201
    return data


def test_authenticate(client: TestClient, credentials: dict):
    r = client.post(
        "/auth/token",
        data={
            "username": credentials["username"],
            "password": credentials["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, r.text
    tok = r.json()["token"]
    assert tok and isinstance(tok, str)


def test_authenticate_with_incorrect_username(client: TestClient, credentials: dict):
    r = client.post(
        "/auth/token",
        data={
            "username": "alex",
            "password": credentials["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 400, r.text


def test_authenticate_with_incorrect_password(client: TestClient, credentials: dict):
    r = client.post(
        "/auth/token",
        data={
            "username": credentials["username"],
            "password": "P@ssW0rd"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 400, r.text
