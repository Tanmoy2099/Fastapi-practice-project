from typing import List
from beanie import PydanticObjectId
from app.core.exceptions import UnprocessableEntityException, NotFoundException, BadRequestException, ConflictException
from app.models.user import User
from app.repositories.user_repo import user_repo

class UserService:
    
    async def get_by_id(self, user_id: str) -> User:
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def follow(self, current_user: User, target_id: str) -> None:
        target = await self.get_by_id(target_id)
        
        if target.id == current_user.id:
            raise BadRequestException("Cannot follow yourself")
            
        if current_user.follows(target.id):
            raise ConflictException("Already following this user")
            
        current_user.following.append(target.id)
        await user_repo.save(current_user)

    async def unfollow(self, current_user: User, target_id: str) -> None:
        target = await self.get_by_id(target_id)
        
        if not current_user.follows(target.id):
            raise NotFoundException("Not following this user")
            
        current_user.following.remove(target.id)
        await user_repo.save(current_user)

    async def get_following(self, user_id: str) -> List[User]:
        user = await self.get_by_id(user_id)
        if not user.following:
            return []
        return await user_repo.get_following_users(user.following)

    async def get_followers(self, user_id: str) -> List[User]:
        target = await self.get_by_id(user_id)
        return await user_repo.get_followers(target.id)

user_service = UserService()
