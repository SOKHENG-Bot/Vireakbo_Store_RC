from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import databaseManager
from app.core.settings import getSettings
from app.services.userService import UserService
from app.utils.jwtHandler import JWTHandler

# JWT Handler instance
jwtHandler = JWTHandler(
    secretKey=getSettings.SECRET_KEY, algorithm=getSettings.ALGORITHM
)


# Database dependency to get an async session
async def getAsyncSession() -> AsyncGenerator[AsyncSession, None]:
    """Get asynchronous database session"""
    async with databaseManager.asyncSessionMaker() as session:
        yield session


# UserService dependency
def getUserService(
    session: AsyncSession = Depends(getAsyncSession),
) -> UserService:
    """Get UserService dependency"""
    return UserService(session=session)


# Get current user ID from JWT token in cookies
async def getCurrentUserId(request: Request) -> str:
    """Get current user ID from JWT token in cookies"""
    accessToken = request.cookies.get("accessToken")
    if not accessToken:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token not found in cookies",
        )

    try:
        tokenData = jwtHandler.decodeToken(accessToken)
        return str(tokenData.userId)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}"
        )


# Common dependencies alias
databaseDep = Depends(getAsyncSession)
currentUserIdDep = Depends(getCurrentUserId)

# UserService dependency alias
userServiceDep = Depends(getUserService)
