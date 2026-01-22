import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum
from starlette import status

class ProductMini(BaseModel):
    id: int
    title: str
    description: str | None = None
    slug: str
    image: str | None = None
    price: float
    stock_quantity: int
    created_at: datetime

    class Config:
        from_attributes = True


class CartItemMini(BaseModel):
    id: int
    quantity: int
    price: float
    product: ProductMini

    class Config:
        from_attributes = True

class cart_Item_base(BaseModel):
    quantity:int
    product:int


class CartResponse(BaseModel):
    id: int
    user_id: int
    total_price: float
    items: list[CartItemMini]

    class Config:
        from_attributes = True



