from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import ServiceBase


class Order(ServiceBase):
    __tablename__ = "orders"

    # Order fields
    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    userId: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.Id"), unique=True, nullable=False
    )
    productName: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    pricePerUnit: Mapped[float] = mapped_column(Float, nullable=False)
    totalPrice: Mapped[float] = mapped_column(Float, nullable=False)

    # Timestamps
    orderedAt: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    # Relationships
    users = relationship("User", back_populates="orders")

    # Representation
    def __repr__(self) -> str:
        return f"<Order Id={self.Id} userId={self.userId} productName={self.productName} quantity={self.quantity} totalPrice={self.totalPrice} orderedAt={self.orderedAt}>"
