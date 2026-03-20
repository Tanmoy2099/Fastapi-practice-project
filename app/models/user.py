from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import EmailStr, Field
from beanie import PydanticObjectId


class User(Document):
    email: EmailStr
    username: str
    hashed_password: str
    role: str = "user"                          # "user" | "admin"
    following: list[PydanticObjectId] = []      # user IDs this user follows
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        indexes = [
            "email",      # unique enforced at app layer with find_one checks
            "username",
        ]

    def is_admin(self) -> bool:
        return self.role == "admin"

    def follows(self, user_id: PydanticObjectId) -> bool:
        return user_id in self.following
