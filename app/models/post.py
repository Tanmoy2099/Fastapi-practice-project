from datetime import datetime
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field


class Post(Document):
    title: str
    content: str
    author_id: PydanticObjectId
    published: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "posts"
        use_revision = True

    def publish(self) -> None:
        self.published = True
        self.updated_at = datetime.utcnow()

    def unpublish(self) -> None:
        self.published = False
        self.updated_at = datetime.utcnow()

    def is_owned_by(self, user_id: PydanticObjectId) -> bool:
        return self.author_id == user_id
