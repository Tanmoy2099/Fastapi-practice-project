from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field


class Post(Document):
    """
    Mongoose-style document model for a Post.
    Beanie = pydantic schema + MongoDB document + business logic in one class.
    """

    title: str
    content: str
    author: str
    published: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "posts"          # MongoDB collection name
        use_revision = True     # optimistic concurrency control

    def publish(self) -> None:
        """Business logic: publish the post."""
        self.published = True
        self.updated_at = datetime.utcnow()

    def unpublish(self) -> None:
        """Business logic: unpublish the post."""
        self.published = False
        self.updated_at = datetime.utcnow()
