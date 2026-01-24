from decimal import Decimal
from typing import List,Optional
from enum import Enum as PyEnum
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy.orm import Mapped,MappedColumn,relationship
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, Enum, Numeric
from datetime import datetime,timedelta,timezone
from app.db.base import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product
    from app.models.payment import PaymentModel
    from app.models.shipping_model import ShippingModel,ShippingStatus,Shipping_Status



class OrderStatus(str, PyEnum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class OrderItem(Base):
    __tablename__ = "order_item"
    id:Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)
    order_id:Mapped[int] = MappedColumn(Integer, ForeignKey("order.id", ondelete="CASCADE"), nullable=False)
    product_id:Mapped[int | None] = MappedColumn(Integer, ForeignKey("product.id", ondelete="SET NULL"), nullable=True)
    price:Mapped[float] = MappedColumn(Numeric(10,2), nullable=False)
    quantity:Mapped[int] = MappedColumn(Numeric(10,2), nullable=False)
    created_at:Mapped[datetime] = MappedColumn(DateTime, default=func.now(), nullable=False)

    order:Mapped["Order"] = relationship("Order", back_populates="order_item")
    product:Mapped[Optional["Product"]]= relationship("Product", lazy="selectin")



class Order(Base):

    __tablename__ = "order"
    id:Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)
    user_id:Mapped[int] = MappedColumn(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    total_price:Mapped[float] = MappedColumn(Numeric(10,2), nullable=False)
    status:Mapped[OrderStatus] = MappedColumn(Enum(OrderStatus),default=OrderStatus.pending, nullable=False)
    shipping_address_id:Mapped[int] = MappedColumn(Integer, ForeignKey("shipping_model.id", ondelete="CASCADE"), nullable=False)
    created_at:Mapped[datetime] = MappedColumn(DateTime, default=func.now(), nullable=False)

    order_item:Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order")
    shipping_model:Mapped["ShippingModel"] = relationship("ShippingModel", back_populates="order")
    user:Mapped["User"] = relationship("User", back_populates="order")
    Shipping_Status:Mapped["Shipping_Status"] = relationship("Shipping_Status", back_populates="order")
    payment_model:Mapped["PaymentModel"] = relationship("PaymentModel", back_populates="order")

