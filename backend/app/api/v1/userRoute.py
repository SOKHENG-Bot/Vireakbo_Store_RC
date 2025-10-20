import logging

from app.api.dependency import currentUserIdDep, databaseDep, userServiceDep
from app.schemas.userSchema import (
    MessageResponseSchema,
    UserChangePasswordSchema,
    UserCreateSchema,
    UserForgotPasswordSchema,
    UserLoginSchema,
    UserResetPasswordSchema,
    VerifyOtpSchema,
)
from app.services.userService import UserService
from fastapi import APIRouter, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

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
    "/verifyOtp",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def verifyOtp(
    data: VerifyOtpSchema,
    service: UserService = userServiceDep,
    db: AsyncSession = databaseDep,
) -> MessageResponseSchema:
    try:
        await service.verifyUserOtp(data)
        logger.info(
            f"OTP verified successfully for: {data.phoneNumber}",
        )
        return MessageResponseSchema(message="OTP verified successfully")
    except Exception as e:
        logger.error(
            f"Error verifying OTP for {data.phoneNumber}: {str(e)}",
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
    "/forgotPassword",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def forgotPassword(
    data: UserForgotPasswordSchema,
    service: UserService = userServiceDep,
    db: AsyncSession = databaseDep,
) -> MessageResponseSchema:
    try:
        await service.forgotPassword(data)
        logger.info(
            f"Password reset OTP sent successfully to: {data.phoneNumber}",
        )
        return MessageResponseSchema(message="Password reset OTP sent successfully")
    except Exception as e:
        logger.error(
            f"Error sending password reset OTP to {data.phoneNumber}: {str(e)}",
        )
        raise


@userRoutes.post(
    "/resetPassword",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def resetPassword(
    data: UserResetPasswordSchema,
    service: UserService = userServiceDep,
    db: AsyncSession = databaseDep,
) -> MessageResponseSchema:
    try:
        await service.resetPassword(data)
        logger.info(
            f"Password reset successfully for: {data.phoneNumber}",
        )
        return MessageResponseSchema(message="Password reset successfully")
    except Exception as e:
        logger.error(
            f"Error resetting password for {data.phoneNumber}: {str(e)}",
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
