import pytest
from fastapi.testclient import TestClient

def create_user(client: TestClient, n: int):
    payload = {"email": f"user{n}@example.com", "username": f"user{n}", "password": "Password123!"}
    res = client.post("/api/v1/auth/register", json=payload)
    tokens = res.json()
    prof = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    return tokens, prof.json()


def test_get_me(client: TestClient):
    tokens, prof = create_user(client, 1)
    assert "email" in prof


def test_follow_and_unfollow(client: TestClient):
    tokens_A, prof_A = create_user(client, 2)
    tokens_B, prof_B = create_user(client, 3)

    headers_A = {"Authorization": f"Bearer {tokens_A['access_token']}"}

    # Follow
    res = client.post(f"/api/v1/users/{prof_B['id']}/follow", headers=headers_A)
    assert res.status_code == 204

    # Duplicate Follow 
    res = client.post(f"/api/v1/users/{prof_B['id']}/follow", headers=headers_A)
    assert res.status_code == 409

    # Cannot follow self
    res = client.post(f"/api/v1/users/{prof_A['id']}/follow", headers=headers_A)
    assert res.status_code == 400

    # Ensure followers list is populated
    res = client.get(f"/api/v1/users/{prof_B['id']}/followers")
    assert any(u["id"] == prof_A["id"] for u in res.json())

    # Unfollow
    res = client.delete(f"/api/v1/users/{prof_B['id']}/follow", headers=headers_A)
    assert res.status_code == 204

    # Ensure followers list is empty
    res = client.get(f"/api/v1/users/{prof_B['id']}/followers")
    assert not any(u["id"] == prof_A["id"] for u in res.json())
