from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    content: str


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None


class PostResponse(BaseModel):
    id: str
    title: str
    content: str
    published: bool
    author_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
