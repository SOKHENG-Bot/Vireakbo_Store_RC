import logging

from fastapi import APIRouter, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependency import currentUserIdDep, databaseDep, userServiceDep
from app.schemas.userSchema import (
    MessageResponseSchema,
    UserChangePasswordSchema,
    UserCreateSchema,
    UserLoginSchema,
)
from app.services.userService import UserService

userRoutes = APIRouter()

logger = logging.getLogger(__name__)


@userRoutes.post(
    "/register",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreateSchema,
    service: UserService = userServiceDep,
    db: AsyncSession = databaseDep,
) -> MessageResponseSchema:
    try:
        await service.registerUser(data)
        logger.info(
            f"User registered successfully: {data.phoneNumber}",
        )
        return MessageResponseSchema(message="User registered successfully")
    except Exception as e:
        logger.error(
            f"Error registering user {data.phoneNumber}: {str(e)}",
        )
        raise


@userRoutes.post(
    "/login",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def login(
    response: Response,
    data: UserLoginSchema,
    service: UserService = userServiceDep,
    db: AsyncSession = databaseDep,
) -> MessageResponseSchema:
    try:
        await service.authenticateUser(data, response)
        logger.info(
            f"User logged in successfully: {data.phoneNumber}",
        )
        return MessageResponseSchema(message="User logged in successfully")
    except Exception as e:
        logger.error(
            f"Error logging in user {data.phoneNumber}: {str(e)}",
        )
        raise


@userRoutes.post(
    "/changePassword",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def changePassword(
    data: UserChangePasswordSchema,
    service: UserService = userServiceDep,
    currentUserId: int = currentUserIdDep,
    db: AsyncSession = databaseDep,
) -> MessageResponseSchema:
    try:
        await service.changePassword(currentUserId, data)
        logger.info(
            f"User password changed successfully: {currentUserId}",
        )
        return MessageResponseSchema(message="Password changed successfully")
    except Exception as e:
        logger.error(
            f"Error changing password for user {currentUserId}: {str(e)}",
        )
        raise
