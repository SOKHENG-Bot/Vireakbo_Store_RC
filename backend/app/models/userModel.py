from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import ServiceBase


class User(ServiceBase):
    __tablename__ = "users"

    # Authentication fields
    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fullName: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    phoneNumber: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    hashedPassword: Mapped[str] = mapped_column(String, nullable=False)

    # Status fields
    isVerified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    createdAt: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    lastLoginAt: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc), nullable=True
    )

    # Relationships
    orders = relationship("Order", back_populates="users")

    # Representation
    def __repr__(self) -> str:
        return f"<User id={self.Id} full_name={self.fullName} phone_number={self.phoneNumber} is_verified={self.isVerified} created_at={self.createdAt}>"
