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
    from app.models.order import OrderItem, Order
    from app.models.shipping_model import ShippingModel,ShippingStatus,Shipping_Status


class PaymentStatus(str, PyEnum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELED = "CANCELED"

class PaymentGateway(str, PyEnum):
    mock = "mock"
    razorpay = "razorpay"

class PaymentModel(Base):
    __tablename__ = "payment_model"
    id:Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)
    order_id:Mapped[int] = MappedColumn(Integer, ForeignKey("order.id", ondelete="CASCADE"),nullable=False)
    user_id:Mapped[int] = MappedColumn(Integer, ForeignKey("user.id", ondelete="CASCADE"),nullable=False)
    amount:Mapped[float] = MappedColumn(Numeric(10,2),nullable=False)
    status:Mapped[PaymentStatus] = MappedColumn(Enum(PaymentStatus),nullable=False,default=PaymentStatus.PENDING)
    payment_gateway:Mapped[PaymentGateway] = MappedColumn(Enum(PaymentGateway),nullable=False,default=PaymentGateway.mock)
    is_paid:Mapped[bool] = MappedColumn(Boolean,nullable=False,default=False)

    payment_gateway_order_id:Mapped[str|None] = MappedColumn(String(255),nullable=True,default=None)
    payment_gateway_id:Mapped[str|None] = MappedColumn(String(255),nullable=True,default=None)
    payment_gateway_signature:Mapped[str|None] = MappedColumn(String(255),nullable=True,default=None)
    updated_at:Mapped[datetime] = MappedColumn(DateTime,nullable=True,default=None)


    order:Mapped["Order"] = relationship("Order", back_populates="payment_model")
    user:Mapped["User"] = relationship("User", back_populates="payment_model")