from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.userModel import User


class UserRepository:
    """Repository for user-related database operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def queryId(self, userId: int) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.Id == userId))
        return result.scalar_one_or_none()

    async def queryPhoneNumber(self, phoneNumber: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.phoneNumber == phoneNumber)
        )
        return result.scalar_one_or_none()

    async def create(self, userData: User) -> User:
        user = User(**userData)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, userData: User) -> User:
        await self.session.commit()
        await self.session.refresh(userData)
        return userData

    async def delete(self, userData: User) -> None:
        await self.session.delete(userData)
        await self.session.commit()
