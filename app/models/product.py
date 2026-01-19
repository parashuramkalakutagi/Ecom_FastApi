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


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id: Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = MappedColumn(
        ForeignKey("product.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[int] = MappedColumn(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )



class Product(Base):
    __tablename__ = "product"

    id:Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)
    title:Mapped[str] = MappedColumn(String(255), nullable=False)
    description:Mapped[str] = MappedColumn(String(255), nullable=False)
    image:Mapped[str] = MappedColumn(String(255), nullable=True)
    price:Mapped[float] = MappedColumn(Numeric(10, 2), default=0.00)
    slug:Mapped[str] = MappedColumn(String(255),unique=True,nullable=False)
    stock_quantity:Mapped[int] = MappedColumn(Integer,default=0)
    created_at:Mapped[datetime] = MappedColumn(DateTime,default=datetime.now,nullable=False)

    #  Many-to-Many relationship
    categories: Mapped[list["Category"]] = relationship(
        "Category",
        secondary="product_categories",
        back_populates="products",
        lazy="selectin"
    )


class Category(Base):
    __tablename__ = "categories"
    id:Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)
    name:Mapped[str] = MappedColumn(String(255), nullable=False)

    #  Many-to-Many relationship
    products: Mapped[list["Product"]] = relationship(
        "Product",
        secondary="product_categories",
        back_populates="categories",
        lazy="selectin"
    )