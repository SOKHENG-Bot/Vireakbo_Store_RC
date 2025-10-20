import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from fastapi import HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SecurityManager
from app.core.settings import getSettings
from app.models.otpModel import OTP
from app.models.userModel import User
from app.provider.smsProvider import smsService
from app.repository.otpRepo import OTPRepository
from app.repository.userRepo import UserRepository
from app.schemas.userSchema import (
    UserChangePasswordSchema,
    UserCreateSchema,
    UserForgotPasswordSchema,
    UserLoginSchema,
    UserResetPasswordSchema,
    VerifyOtpSchema,
)
from app.utils.jwtHandler import JWTHandler

logger = logging.getLogger(__name__)
jwtHandler = JWTHandler(
    secretKey=getSettings.SECRET_KEY, algorithm=getSettings.ALGORITHM
)


class UserService:
    """Service for managing user operations"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.userRepository = UserRepository(session)
        self.otpRepository = OTPRepository(session)

    async def registerUser(self, userData: UserCreateSchema) -> User:
        """Register a new user and send OTP"""
        try:
            existingUser = await self.userRepository.queryPhoneNumber(
                userData.phoneNumber
            )
            if existingUser:
                logger.warning(
                    "Registeration failed: Phone number already in use",
                    extra={"phone_number": userData.phoneNumber},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already in use",
                )
            user = User(
                fullName=userData.fullName,
                phoneNumber=userData.phoneNumber,
                hashedPassword=SecurityManager.hashPassword(userData.password),
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)

            otpCode = SecurityManager.generateOTP()
            otp = OTP(
                phoneNumber=userData.phoneNumber,
                otpCode=otpCode,
                expiresAt=datetime.now(timezone.utc) + timedelta(minutes=5),
            )
            await self.otpRepository.create(otp)
            try:
                await smsService.sendSms(
                    userData.phoneNumber,
                    f"Your Vireakbo RC Store verification code is: {otpCode}. Valid for 5 minutes.",
                )
            except Exception as e:
                logger.error(
                    f"Error sending OTP SMS during registration: {e}",
                    extra={"phone_number": userData.phoneNumber},
                )
            logger.info(
                "User registered successfully with OTP sent",
                extra={"userId": user.Id, "phone_number": userData.phoneNumber},
            )
            return user

        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(
                f"Error during user registration: {e}",
                extra={"phone_number": userData.phoneNumber},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error during registration: {e}",
            )

    async def verifyUserOtp(self, data: VerifyOtpSchema) -> None:
        """Verify user's phone number using OTP and delete it from database"""
        try:
            otpRecord = await self.otpRepository.getValidOTP(data.phoneNumber)
            if not otpRecord:
                logger.warning(
                    "OTP verification failed: No valid OTP found",
                    extra={"phone_number": data.phoneNumber},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired OTP",
                )
            if otpRecord.otpCode != data.otpCode:
                logger.warning(
                    "OTP verification failed: Invalid OTP code",
                    extra={"phone_number": data.phoneNumber},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid OTP code",
                )

            user = await self.userRepository.queryPhoneNumber(data.phoneNumber)
            if user:
                user.isVerified = True
                await self.session.commit()
            await self.otpRepository.deleteOTP(otpRecord.Id)

            logger.info(
                "OTP verified successfully and deleted from database",
                extra={"phone_number": data.phoneNumber},
            )
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(
                f"Error during OTP verification: {e}",
                extra={"phone_number": data.phoneNumber},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error during OTP verification: {e}",
            )

    async def authenticateUser(
        self, userData: UserLoginSchema, response: Response
    ) -> User:
        """Authenticate user using phone number and password"""
        try:
            user = await self.userRepository.queryPhoneNumber(userData.phoneNumber)
            if not user or not SecurityManager.verifyPassword(
                userData.password, user.hashedPassword
            ):
                logger.warning(
                    "Authentication failed: Invalid credentials",
                    extra={"phone_number": userData.phoneNumber},
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid phone number or password",
                )
            tokenData: Dict[str, Any] = {
                "userId": user.Id,
                "phoneNumber": user.phoneNumber,
                "fullName": user.fullName,
            }
            accessToken = jwtHandler.encodeToken(
                tokenData,
                expiresDelta=timedelta(minutes=getSettings.ACCESS_TOKEN_EXPIRE_MINUTES),
            )
            response.set_cookie(
                key="accessToken",
                value=accessToken,
                httponly=True,
                max_age=getSettings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                secure=True,
                samesite="lax",
            )
            logger.info(
                "User authenticated successfully",
                extra={"userId": user.Id, "phone_number": userData.phoneNumber},
            )
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error during user authentication: {e}",
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error during authentication: {e}",
            )

    async def forgotPassword(self, data: UserForgotPasswordSchema) -> None:
        """Initiate password reset process"""
        try:
            user = await self.userRepository.queryPhoneNumber(data.phoneNumber)
            if not user:
                logger.warning(
                    "Forgot password failed: User not found",
                    extra={"phone_number": data.phoneNumber},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User with given phone number not found",
                )
            logger.info(
                "Password reset initiated",
                extra={"userId": user.Id, "phone_number": data.phoneNumber},
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error during forgot password process: {e}",
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error during forgot password process: {e}",
            )

    async def resetPassword(self, data: UserResetPasswordSchema) -> None:
        """Reset user password using phone number and new password"""
        try:
            user = await self.userRepository.queryPhoneNumber(data.phoneNumber)
            if not user:
                logger.warning(
                    "Reset password failed: User not found",
                    extra={"phone_number": data.phoneNumber},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User with given phone number not found",
                )
            user.hashedPassword = SecurityManager.hashPassword(data.newPassword)
            await self.userRepository.update(user)
            logger.info(
                "Password reset successfully",
                extra={"userId": user.Id, "phone_number": data.phoneNumber},
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error during password reset: {e}",
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error during password reset: {e}",
            )

    async def changePassword(self, currentUserId: int, data: UserChangePasswordSchema):
        """Change user password using user ID and old/new passwords"""
        try:
            # Get user from database using userId
            user = await self.userRepository.queryId(int(currentUserId))
            if not user:
                logger.warning(
                    "Change password failed: User not found",
                    extra={"userId": currentUserId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User with given ID not found",
                )

            if not SecurityManager.verifyPassword(
                data.oldPassword, user.hashedPassword
            ):
                logger.warning(
                    "Change password failed: Incorrect old password",
                    extra={"userId": currentUserId},
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect old password",
                )

            user.hashedPassword = SecurityManager.hashPassword(data.newPassword)
            await self.userRepository.update(user)
            logger.info(
                "Password changed successfully",
                extra={"userId": user.Id},
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error during password change: {e}",
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error during password change: {e}",
            )

    async def logoutUser(self, currentUser: User, response: Response) -> None:
        """Logout current user"""
        try:
            if not currentUser:
                logger.warning(
                    "Logout failed: User is not authenticated",
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User is not authenticated",
                )
            response.delete_cookie(key="accessToken")
            logger.info(
                "User logged out successfully",
                extra={"phone_number": currentUser.phoneNumber},
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error during user logout: {e}",
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error during logout: {e}",
            )
