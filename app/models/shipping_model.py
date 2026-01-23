from decimal import Decimal
from typing import List,Optional
import enum
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
    from app.models.order import Order

class ShippingStatus(str,enum.Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delevered = "delevered"
    cancelled = "cancelled"


class ShippingModel(Base):
    __tablename__ = "shipping_model"
    id:Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)
    user_id:Mapped[int] = MappedColumn(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    name:Mapped[str] = MappedColumn(String(255), nullable=False)
    address:Mapped[str] = MappedColumn(String(255), nullable=False)
    city:Mapped[str] = MappedColumn(String(255), nullable=False)
    phone:Mapped[str] = MappedColumn(String(255), nullable=False)
    email:Mapped[str] = MappedColumn(String(255), nullable=False)
    state:Mapped[str] = MappedColumn(String(255), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="shipping_model")
    order:Mapped["Order"] = relationship("Order", back_populates="shipping_model")


class Shipping_Status(Base):
    __tablename__ = "shipping_status"
    id:Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)
    order_id:Mapped[int] = MappedColumn(Integer, ForeignKey("order.id", ondelete="CASCADE"))
    status:Mapped[ShippingStatus] = MappedColumn(Enum(ShippingStatus), default=ShippingStatus.pending)
    update_at:Mapped[datetime] = MappedColumn(DateTime, default=datetime.now)

    order:Mapped["Order"] = relationship("Order", back_populates="Shipping_Status")