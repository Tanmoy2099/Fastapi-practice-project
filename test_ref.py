import httpx
import asyncio

async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Register
        payload = {"email": "ref-test-bug@example.com", "username": "reftestbug", "password": "Password123!"}
        # Ignore 409 if already exists
        await client.post("/api/v1/auth/register", json=payload)
        
        # Login
        res = await client.post("/api/v1/auth/login", json={"email": "ref-test-bug@example.com", "password": "Password123!"})
        print(f"Login status: {res.status_code}")
        
        # Verify /me works initially
        access = res.json()["access_token"]
        res_me = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {access}"})
        print(f"Initial /me: {res_me.status_code}")
        
        # Refresh
        # httpx handles cookies automatically in the AsyncClient!
        res_ref = await client.post("/api/v1/auth/refresh")
        print(f"Refresh status: {res_ref.status_code}")
        if res_ref.status_code == 200:
            new_access = res_ref.json()["access_token"]
            print("Access tokens identical?", access == new_access)
            
            # Verify /me with new token
            res_me_new = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {new_access}"})
            print(f"New /me status: {res_me_new.status_code}")
            if res_me_new.status_code != 200:
                print("Error:", res_me_new.json())

asyncio.run(main())
