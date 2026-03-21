from typing import List, Optional
from beanie import PydanticObjectId
from app.models.user import User

class UserRepository:
    """Encapsulates all database operations for the User model."""

    async def find_by_email(self, email: str) -> Optional[User]:
        return await User.find_one(User.email == email)

    async def find_by_username(self, username: str) -> Optional[User]:
        return await User.find_one(User.username == username)

    async def get_by_id(self, user_id: str | PydanticObjectId) -> Optional[User]:
        if isinstance(user_id, str):
            try:
                user_id = PydanticObjectId(user_id)
            except Exception:
                return None
        return await User.get(user_id)

    async def create(self, user: User) -> User:
        return await user.insert()

    async def save(self, user: User) -> User:
        return await user.save()

    async def get_following_users(self, following_ids: List[PydanticObjectId]) -> List[User]:
        return await User.find({"_id": {"$in": following_ids}}).to_list()

    async def get_followers(self, user_id: PydanticObjectId) -> List[User]:
        return await User.find({"following": user_id}).to_list()

user_repo = UserRepository()
