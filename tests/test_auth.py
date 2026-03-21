import pytest
from fastapi.testclient import TestClient

def test_register_success(client: TestClient):
    payload = {"email": "test@example.com", "username": "testuser", "password": "Password123!"}
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201
    assert "access_token" in res.json()
    assert "refresh_token" in res.cookies  # Prove cookie is set natively


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
    assert "refresh_token" in res.cookies


def test_login_invalid_password(client: TestClient):
    payload = {"email": "loginfail@example.com", "username": "loginfail", "password": "Password123!"}
    client.post("/api/v1/auth/register", json=payload)
    
    res = client.post("/api/v1/auth/login", json={"email": "loginfail@example.com", "password": "WrongPassword"})
    assert res.status_code == 401


def test_refresh_token(client: TestClient):
    payload = {"email": "ref@example.com", "username": "ref", "password": "Password123!"}
    res = client.post("/api/v1/auth/register", json=payload)
    
    # Extract the cookie manually set by the register logic
    refresh_cookie = res.cookies.get("refresh_token")
    assert refresh_cookie is not None

    # TestClient normally persists cookies, but we explicitly set it to prove the flow
    refresh_res = client.post("/api/v1/auth/refresh", cookies={"refresh_token": refresh_cookie})
    assert refresh_res.status_code == 200
    assert "access_token" in refresh_res.json()
    assert refresh_res.cookies.get("refresh_token") != refresh_cookie  # Prove rotation happened


def test_logout(client: TestClient):
    payload = {"email": "logout1@example.com", "username": "logout1", "password": "Password123!"}
    res = client.post("/api/v1/auth/register", json=payload)
    
    access = res.json()["access_token"]
    refresh = res.cookies.get("refresh_token")
    
    headers = {"Authorization": f"Bearer {access}"}
    logout_res = client.post("/api/v1/auth/logout", headers=headers, cookies={"refresh_token": refresh})
    assert logout_res.status_code == 204

    # Using refresh token should now fail natively
    refresh_res = client.post("/api/v1/auth/refresh", cookies={"refresh_token": refresh})
    assert refresh_res.status_code == 401


def test_logout_and_revoke_all(client: TestClient):
    payload = {"email": "logout@example.com", "username": "logout", "password": "Password123!"}
    res = client.post("/api/v1/auth/register", json=payload)
    
    access = res.json()["access_token"]
    refresh = res.cookies.get("refresh_token")
    
    headers = {"Authorization": f"Bearer {access}"}
    logout_res = client.post("/api/v1/auth/logout-all", headers=headers)
    assert logout_res.status_code == 204

    refresh_res = client.post("/api/v1/auth/refresh", cookies={"refresh_token": refresh})
    assert refresh_res.status_code == 401


# ── Negative Testing Edge Cases ───────────────────────────────────────────────

def test_register_invalid_email_format(client: TestClient):
    payload = {"email": "not-an-email", "username": "bademail", "password": "Password123!"}
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 422


def test_login_unregistered_email(client: TestClient):
    res = client.post("/api/v1/auth/login", json={"email": "ghost@example.com", "password": "Password123!"})
    assert res.status_code == 401


def test_invalid_refresh_token(client: TestClient):
    res = client.post("/api/v1/auth/refresh", cookies={"refresh_token": "fake.jwt.token.data"})
    assert res.status_code == 401
