from datetime import datetime
from enum import Enum

from beanie import Document, PydanticObjectId
from pydantic import EmailStr, Field


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(Document):
    email: EmailStr
    username: str
    hashed_password: str
    role: UserRole = UserRole.USER
    following: list[PydanticObjectId] = []  # user IDs this user follows
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        indexes = [
            "email",  # unique enforced at app layer with find_one checks
            "username",
        ]

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def follows(self, user_id: PydanticObjectId) -> bool:
        return user_id in self.following
