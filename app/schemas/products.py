import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum

from pydantic_extra_types.phone_numbers import PhoneNumber
from starlette import status

# class CategoryProducts(BaseModel):
#     title: str
#     description: str
#     price: float
#     slug: str
#     stock_quantity: int
#     category_ids: List[int]
#     image: Optional[str]
#     created_at: datetime
#
#     class Config:
#         from_attributes = True


class ProductMini(BaseModel):
    id: int
    title: str
    description: str | None = None

    class Config:
        orm_mode = True


class CategoryResponses(BaseModel):
    id: int
    name: str
    products: list[ProductMini]

    class Config:
        orm_mode = True


class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
   pass

class CategoryResponse(CategoryBase):
    id:int
    name: str


    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    title: str
    description: str
    price: float
    slug: str
    stock_quantity: int

class ProductCreate(ProductBase):
    category_ids: List[int]

class ProductResponse(ProductBase):
    id: int
    image: Optional[str]
    created_at: datetime
    categories: List[CategoryResponse]  # nested response

    class Config:
        from_attributes = True



