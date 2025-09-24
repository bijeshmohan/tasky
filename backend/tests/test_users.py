from fastapi.testclient import TestClient

from api.schemas.user import UserRead


def test_signup(client: TestClient):
    username = "alice"
    password = "secret"
    r = client.post(
        "/users",
        json={"username": username, "password": password}
    )
    assert r.status_code == 201
    validated = UserRead(**r.json())
    assert validated.id is not None
    assert validated.username == username
    assert validated.created is not None


def test_signup_with_short_username(client: TestClient):
    username = "un"
    password = "secret"
    r = client.post(
        "/users",
        json={"username": username, "password": password}
    )
    assert r.status_code == 422


def test_signup_with_long_username(client: TestClient):
    username = "blahblahblahblahblahh"
    password = "secret"
    r = client.post(
        "/users",
        json={"username": username, "password": password}
    )
    assert r.status_code == 422
