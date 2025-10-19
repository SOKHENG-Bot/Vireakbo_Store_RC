from random import randint

from passlib.context import CryptContext

pwdContext = CryptContext(schemes=["argon2"], deprecated="auto")


class SecurityManager:
    """Security manager for password hashing and verification"""

    @staticmethod
    def hashPassword(password: str) -> str:
        """Hash a plaintext password"""
        return pwdContext.hash(password)

    @staticmethod
    def verifyPassword(plainPassword: str, hashedPassword: str) -> bool:
        """Verify a plaintext password against a hashed password"""
        return pwdContext.verify(plainPassword, hashedPassword)

    @staticmethod
    def generateOTP() -> str:
        """Generate a 6-digit OTP code as a string"""
        otp = f"{randint(0, 999999):06}"
        return otp
