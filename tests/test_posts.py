import pytest
from fastapi.testclient import TestClient

def create_user(client: TestClient, n: int):
    payload = {"email": f"postuser{n}@example.com", "username": f"postuser{n}", "password": "Password123!"}
    res = client.post("/api/v1/auth/register", json=payload)
    tokens = res.json()
    prof = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    return tokens, prof.json()


def test_create_and_update_post(client: TestClient):
    tokens, prof = create_user(client, 1)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # Create Post
    payload = {"title": "Test Post", "content": "This is a test post"}
    res = client.post("/api/v1/posts/", json=payload, headers=headers)
    assert res.status_code == 201
    post_id = res.json()["id"]

    # Update Post
    res = client.put(f"/api/v1/posts/{post_id}", json={"published": True}, headers=headers)
    assert res.status_code == 200
    assert res.json()["published"] is True
    
    # Delete Post
    res = client.delete(f"/api/v1/posts/{post_id}", headers=headers)
    assert res.status_code == 204


def test_post_permissions(client: TestClient):
    tokens_A, prof_A = create_user(client, 2)
    tokens_B, prof_B = create_user(client, 3)

    headers_A = {"Authorization": f"Bearer {tokens_A['access_token']}"}
    headers_B = {"Authorization": f"Bearer {tokens_B['access_token']}"}

    # User A creates a post
    res = client.post("/api/v1/posts/", json={"title": "A's post", "content": "hello"}, headers=headers_A)
    post_id = res.json()["id"]

    # User B tries to update it
    res = client.put(f"/api/v1/posts/{post_id}", json={"title": "Hacked"}, headers=headers_B)
    assert res.status_code == 403

    # User B tries to delete it
    res = client.delete(f"/api/v1/posts/{post_id}", headers=headers_B)
    assert res.status_code == 403


def test_post_feed(client: TestClient):
    tokens_A, prof_A = create_user(client, 4)
    tokens_B, prof_B = create_user(client, 5)

    headers_A = {"Authorization": f"Bearer {tokens_A['access_token']}"}
    headers_B = {"Authorization": f"Bearer {tokens_B['access_token']}"}

    # User B creates a published post
    res = client.post("/api/v1/posts/", json={"title": "B Post", "content": "hi"}, headers=headers_B)
    post_id = res.json()["id"]
    client.put(f"/api/v1/posts/{post_id}", json={"published": True}, headers=headers_B)

    # User A checks feed before following (should be empty)
    res = client.get("/api/v1/posts/feed", headers=headers_A)
    assert len(res.json()) == 0

    # User A follows User B
    client.post(f"/api/v1/users/{prof_B['id']}/follow", headers=headers_A)

    # User A checks feed again (should have B's post)
    res = client.get("/api/v1/posts/feed", headers=headers_A)
    feed = res.json()
    assert len(feed) > 0
    assert any(p["id"] == post_id for p in feed)
