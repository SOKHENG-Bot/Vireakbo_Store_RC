from datetime import datetime, timedelta, timezone

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import ServiceBase


class OTP(ServiceBase):
    """Simple OTP model for phone verification"""

    __tablename__ = "otps"

    Id: Mapped[int] = mapped_column(primary_key=True, index=True)
    phoneNumber: Mapped[str] = mapped_column(String, nullable=False, index=True)
    otpCode: Mapped[str] = mapped_column(String(6), nullable=False)
    createdAt: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    expiresAt: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    isUsed: Mapped[bool] = mapped_column(nullable=False, default=False)
