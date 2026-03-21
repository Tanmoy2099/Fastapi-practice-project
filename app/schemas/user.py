from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    role: str
    following_count: int
    is_active: bool


class UserProfile(BaseModel):
    """Public profile — no email exposed."""

    id: str
    username: str
    following_count: int
