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


class Cart_Item(Base):
    __tablename__ = "cart_item"
    id :Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True,index= True)
    user_id :Mapped[int] = MappedColumn(Integer, ForeignKey("user.id",ondelete="CASCADE"),nullable=False)
    product_id :Mapped[int] = MappedColumn(Integer, ForeignKey("product.id",ondelete="SET NULL"),nullable=False)
    quantity :Mapped[int] = MappedColumn(Integer,default=1)
    price :Mapped[float] = MappedColumn(Numeric,default=0)

    user:Mapped["User"] = relationship("User",back_populates="cart_item")
    product:Mapped["Product"] = relationship("Product",back_populates="cart_item")