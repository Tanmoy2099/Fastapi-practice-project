import pytest
from fastapi.testclient import TestClient

def test_register_success(client: TestClient):
    payload = {"email": "test@example.com", "username": "testuser", "password": "Password123!"}
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201
    assert "access_token" in res.json()


def test_register_duplicate_email(client: TestClient):
    payload = {"email": "test@example.com", "username": "other", "password": "Password123!"}
    client.post("/api/v1/auth/register", json=payload)
    
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "CONFLICT"


def test_login_success(client: TestClient):
    payload = {"email": "login@example.com", "username": "loginuser", "password": "Password123!"}
    client.post("/api/v1/auth/register", json=payload)
    
    res = client.post("/api/v1/auth/login", json={"email": "login@example.com", "password": "Password123!"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_invalid_password(client: TestClient):
    payload = {"email": "loginfail@example.com", "username": "loginfail", "password": "Password123!"}
    client.post("/api/v1/auth/register", json=payload)
    
    res = client.post("/api/v1/auth/login", json={"email": "loginfail@example.com", "password": "WrongPassword"})
    assert res.status_code == 401


def test_refresh_token(client: TestClient):
    payload = {"email": "ref@example.com", "username": "ref", "password": "Password123!"}
    res = client.post("/api/v1/auth/register", json=payload)
    refresh_token = res.json()["refresh_token"]

    refresh_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_res.status_code == 200
    assert "access_token" in refresh_res.json()
    assert refresh_res.json()["refresh_token"] != refresh_token


def test_logout_and_revoke_all(client: TestClient):
    payload = {"email": "logout@example.com", "username": "logout", "password": "Password123!"}
    res = client.post("/api/v1/auth/register", json=payload)
    access, refresh = res.json()["access_token"], res.json()["refresh_token"]
    
    # Logout all
    headers = {"Authorization": f"Bearer {access}"}
    logout_res = client.post("/api/v1/auth/logout-all", headers=headers)
    assert logout_res.status_code == 204

    # Using refresh token should now fail
    refresh_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert refresh_res.status_code == 401


# ── Negative Testing Edge Cases ───────────────────────────────────────────────

def test_register_invalid_email_format(client: TestClient):
    payload = {"email": "not-an-email", "username": "bademail", "password": "Password123!"}
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 422  # Pydantic should catch this immediately


def test_login_unregistered_email(client: TestClient):
    # Attempting to login to an account that mathematically does not exist
    res = client.post("/api/v1/auth/login", json={"email": "ghost@example.com", "password": "Password123!"})
    assert res.status_code == 401


def test_invalid_refresh_token(client: TestClient):
    # Providing total garbage to the refresh endpoint to ensure PyJWT decryption rejects it
    res = client.post("/api/v1/auth/refresh", json={"refresh_token": "fake.jwt.token.data"})
    assert res.status_code == 401
