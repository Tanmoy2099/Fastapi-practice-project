from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings


_client: AsyncIOMotorClient | None = None


async def connect_db(document_models: list) -> None:
    """Initialize MongoDB connection and Beanie ODM."""
    global _client
    _client = AsyncIOMotorClient(settings.mongo_uri)
    await init_beanie(
        database=_client[settings.mongo_db_name],
        document_models=document_models,
    )


async def close_db() -> None:
    """Close the MongoDB connection."""
    global _client
    if _client:
        _client.close()
        _client = None
