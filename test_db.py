import asyncio

from motor.motor_asyncio import AsyncIOMotorClient


async def test_dbs():
    client = AsyncIOMotorClient("mongodb://localhost:27018")

    # Check what is in practice_db
    try:
        db = client["practice_db"]
        users = await db["User"].count_documents({})
        posts = await db["Post"].count_documents({})
        print(f"PRACTICE_DB: Users={users}, Posts={posts}")
    except Exception as e:
        print(f"Error reading practice_db: {e}")

    # Check what is in practice_test_db
    try:
        test_db = client["practice_test_db"]
        test_users = await test_db["User"].count_documents({})
        test_posts = await test_db["Post"].count_documents({})
        print(f"PRACTICE_TEST_DB: Users={test_users}, Posts={test_posts}")
    except Exception as e:
        print(f"Error reading test_db: {e}")


asyncio.run(test_dbs())
