from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.otpModel import OTP


class OTPRepository:
    """Repository for OTP operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, otp: OTP) -> OTP:
        """Create a new OTP record"""
        self.session.add(otp)
        await self.session.commit()
        await self.session.refresh(otp)
        return otp

    async def getValidOTP(self, phoneNumber: str) -> Optional[OTP]:
        """Get the most recent valid OTP for phone number"""
        query = (
            select(OTP)
            .where(
                and_(
                    OTP.phoneNumber == phoneNumber,
                    OTP.isUsed.is_(False),
                    OTP.expiresAt > datetime.now(timezone.utc),
                )
            )
            .order_by(OTP.createdAt.desc())
        )

        result = await self.session.execute(query)
        return result.scalars().first()

    async def deleteOTP(self, otpId: int) -> None:
        """Delete OTP by ID"""
        query = delete(OTP).where(OTP.Id == otpId)
        await self.session.execute(query)
        await self.session.commit()
