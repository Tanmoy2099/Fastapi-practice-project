from fastapi.testclient import TestClient


def test_refresh_and_me_scenario(client: TestClient):

    # 1. Register
    payload = {
        "email": "ref-scenario@example.com",
        "username": "ref-scenario",
        "password": "Password123!",
    }
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201

    # Extract token
    access = res.json()["access_token"]
    refresh = res.cookies.get("refresh_token")

    # 2. Assert initial /me works
    headers = {"Authorization": f"Bearer {access}"}
    me_res = client.get("/api/v1/users/me", headers=headers)
    assert me_res.status_code == 200, f"Initial fail: {me_res.json()}"

    # 3. Refresh
    ref_res = client.post("/api/v1/auth/refresh", cookies={"refresh_token": refresh})
    assert ref_res.status_code == 200, f"Refresh fail: {ref_res.json()}"

    new_access = ref_res.json()["access_token"]

    # 4. Assert new /me works
    new_headers = {"Authorization": f"Bearer {new_access}"}
    new_me = client.get("/api/v1/users/me", headers=new_headers)
    assert new_me.status_code == 200, f"Refresh Token /me fail: {new_me.json()}"

    print("SUCCESS: The new access token is perfectly valid.")
