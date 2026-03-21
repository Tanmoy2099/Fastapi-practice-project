from typing import Tuple
from app.core.exceptions import ConflictException, UnauthorizedException, ForbiddenException
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.db.redis import token_store
from app.models.user import User
from app.repositories.user_repo import user_repo

class AuthService:

    async def register(self, email: str, username: str, password: str) -> Tuple[str, str]:
        if await user_repo.find_by_email(email):
            raise ConflictException("Email already registered")
        if await user_repo.find_by_username(username):
            raise ConflictException("Username already taken")

        user = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
        )
        await user_repo.create(user)

        user_id = str(user.id)
        access_token = create_access_token(user_id, user.role)
        refresh_token = create_refresh_token(user_id)
        await token_store.store(user_id, refresh_token)

        return access_token, refresh_token

    async def login(self, email: str, password: str) -> Tuple[str, str]:
        user = await user_repo.find_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid credentials")
        if not user.is_active:
            raise ForbiddenException("Account is inactive")

        user_id = str(user.id)
        access_token = create_access_token(user_id, user.role)
        refresh_token = create_refresh_token(user_id)
        await token_store.store(user_id, refresh_token)

        return access_token, refresh_token

    async def refresh(self, refresh_token: str) -> Tuple[str, str]:
        try:
            user_id, _ = refresh_token.split("::", 1)
        except ValueError:
            raise UnauthorizedException("Invalid refresh token format")

        if not await token_store.is_valid(user_id, refresh_token):
            raise UnauthorizedException("Invalid or expired refresh token")

        user = await user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        # Rotate: revoke old, issue new
        await token_store.revoke(user_id, refresh_token)
        new_access = create_access_token(str(user.id), user.role)
        new_refresh = create_refresh_token(str(user.id))
        await token_store.store(user_id, new_refresh)

        return new_access, new_refresh

    async def logout(self, user_id: str, refresh_token: str | None) -> None:
        if refresh_token:
            await token_store.revoke(user_id, refresh_token)

    async def logout_all(self, user_id: str) -> None:
        await token_store.revoke_all(user_id)

auth_service = AuthService()
