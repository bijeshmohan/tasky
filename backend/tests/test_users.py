from fastapi.testclient import TestClient

from backend.schemas.user import UserRead


def test_signup_with_valid_username_and_strong_password(client: TestClient):
    username = "alice"
    password = "p@55W0rd"
    r = client.post(
        "/users",
        json={"username": username, "password": password}
    )
    assert r.status_code == 201
    validated = UserRead(**r.json())
    assert validated.id is not None
    assert validated.username == username
    assert validated.created is not None


def test_signup_with_existing_username_and_strong_password(client: TestClient):
    username = "alice"
    password = "p@55W0rd"
    r = client.post(
        "/users",
        json={"username": username, "password": password}
    )

    username = "alice"
    password = "p@55W0rd123"
    r = client.post(
        "/users",
        json={"username": username, "password": password}
    )
    assert r.status_code == 400


def test_signup_with_short_username_and_strong_password(client: TestClient):
    username = "un"
    password = "p@55W0rd"
    r = client.post(
        "/users",
        json={"username": username, "password": password}
    )
    assert r.status_code == 422


def test_signup_with_long_username_and_strong_password(client: TestClient):
    username = "blahblahblahblahblahh"
    password = "p@55W0rd"
    r = client.post(
        "/users",
        json={"username": username, "password": password}
    )
    assert r.status_code == 422


def test_signup_with_valid_username_and_short_password(client: TestClient):
    username = "alice"
    password = "p@55Wd#"
    r = client.post(
        "/users",
        json={"username": username, "password": password}
    )
    assert r.status_code == 422


def test_signup_with_valid_username_and_long_password(client: TestClient):
    username = "alice"
    password = "p@55Wd#" * 10
    r = client.post(
        "/users",
        json={"username": username, "password": password}
    )
    assert r.status_code == 422


def test_signup_with_valid_username_and_weak_password(client: TestClient):
    username = "alice"
    password = "password"
    r = client.post(
        "/users",
        json={"username": username, "password": password}
    )
    assert r.status_code == 422
