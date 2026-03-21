import time

import requests

BASE_URL = "http://localhost:8000/api/v1"


def print_step(msg):
    print(f"\\n{'=' * 50}\\n[STEP]: {msg}\\n{'=' * 50}")


def run_tests():
    session = requests.Session()
    ts = int(time.time())

    user_a = {
        "email": f"alice_{ts}@example.com",
        "username": f"alice_{ts}",
        "password": "Password123!",
    }
    user_b = {"email": f"bob_{ts}@example.com", "username": f"bob_{ts}", "password": "Password123!"}

    # 1. Register User A
    print_step("Register User A")
    res = session.post(f"{BASE_URL}/auth/register", json=user_a)
    assert res.status_code == 201, f"Failed: {res.text}"
    tokens_a = res.json()
    assert "access_token" in tokens_a
    print("User A registered.")

    # 2. Login User B (Register then login to verify login endpoint)
    print_step("Register & Login User B")
    res = session.post(f"{BASE_URL}/auth/register", json=user_b)
    assert res.status_code == 201, res.text

    res = session.post(
        f"{BASE_URL}/auth/login", json={"email": user_b["email"], "password": user_b["password"]}
    )
    assert res.status_code == 200, res.text
    tokens_b = res.json()
    print("User B logged in.")

    # 3. Get User Profiles
    print_step("Get Profiles")
    headers_a = {"Authorization": f"Bearer {tokens_a['access_token']}"}
    headers_b = {"Authorization": f"Bearer {tokens_b['access_token']}"}

    res_me_a = session.get(f"{BASE_URL}/users/me", headers=headers_a)
    assert res_me_a.status_code == 200, res_me_a.text
    profile_a = res_me_a.json()
    id_a = profile_a["id"]

    res_me_b = session.get(f"{BASE_URL}/users/me", headers=headers_b)
    assert res_me_b.status_code == 200, res_me_b.text
    id_b = res_me_b.json()["id"]
    print(f"Profiles fetched. A: {id_a}, B: {id_b}")

    # 4. User A follows User B
    print_step("User A follows User B")
    res = session.post(f"{BASE_URL}/users/{id_b}/follow", headers=headers_a)
    assert res.status_code in (200, 204), f"Failed follow: {res.status_code} {res.text}"

    # Verify Following
    res = session.get(f"{BASE_URL}/users/{id_a}/following")
    assert res.status_code == 200
    assert any(u["id"] == id_b for u in res.json()), "User B should be in A's following list"

    res = session.get(f"{BASE_URL}/users/{id_b}/followers")
    assert res.status_code == 200
    assert any(u["id"] == id_a for u in res.json()), "User A should be in B's followers list"
    print("Follow system verified.")

    # 5. User B Creates Post
    print_step("User B creates a post")
    post_payload = {"title": "Hello World", "content": "This is Bob's first post"}
    res = session.post(f"{BASE_URL}/posts/", json=post_payload, headers=headers_b)
    assert res.status_code == 201, res.text
    post_id = res.json()["id"]

    # User B Updates Post to published
    res = session.put(f"{BASE_URL}/posts/{post_id}", json={"published": True}, headers=headers_b)
    assert res.status_code == 200, res.text
    print("Post created and published.")

    # 6. User A Gets Feed
    print_step("User A checks feed")
    res = session.get(f"{BASE_URL}/posts/feed", headers=headers_a)
    assert res.status_code == 200, res.text
    feed = res.json()
    assert len(feed) > 0, "Feed should not be empty"
    assert any(p["id"] == post_id for p in feed), "Bob's post should be in Alice's feed"
    print("Feed successfully populated.")

    # 7. Unfollow user
    print_step("User A unfollows User B")
    res = session.delete(f"{BASE_URL}/users/{id_b}/follow", headers=headers_a)
    assert res.status_code in (200, 204), f"Failed unfollow: {res.status_code} {res.text}"

    # Feed should be empty or at least not contain new posts, but let's test refresh token instead

    # 8. Refresh Token
    print_step("Refresh User A's Token")
    rt = tokens_a["refresh_token"]
    res = session.post(f"{BASE_URL}/auth/refresh", json={"refresh_token": rt})
    assert res.status_code == 200, res.text
    new_tokens_a = res.json()
    assert new_tokens_a["access_token"] != tokens_a["access_token"]
    assert new_tokens_a["refresh_token"] != rt
    print("Refresh token rotated successfully.")

    # 9. Logout All
    print_step("User A Logs Out Everywhere")
    new_headers_a = {"Authorization": f"Bearer {new_tokens_a['access_token']}"}
    res = session.post(f"{BASE_URL}/auth/logout-all", headers=new_headers_a)
    assert res.status_code in (200, 204), f"Failed logout-all: {res.status_code} {res.text}"

    # Verify strict refresh denial
    res = session.post(
        f"{BASE_URL}/auth/refresh", json={"refresh_token": new_tokens_a["refresh_token"]}
    )
    assert res.status_code == 401, "Expected 401 after logout-all"
    print("Logout-all successfully invalidated refresh token.")

    print_step("ALL E2E TESTS PASSED SUCCESSFULLY! ✅")


if __name__ == "__main__":
    run_tests()
