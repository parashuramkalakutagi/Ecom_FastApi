import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum

from pydantic_extra_types.phone_numbers import PhoneNumber
from starlette import status


class ProductMini(BaseModel):
    id: int
    title: str
    description: str | None = None

    class Config:
        from_attributes = True


class CategoryResponses(BaseModel):
    id: int
    name: str
    products: list[ProductMini]

    class Config:
        from_attributes = True


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

class PaginatedProductResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: list[ProductResponse]


class DeleteResponse(BaseModel):
    msg: str

# class ProductUpdate(BaseModel):
#     title: str | None
#     description: str | None
#     price: float | None
#     slug: str | None
#     stock_quantity: int | None
#     category_ids: List[int] | None


class ProductPatch(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    category_ids: Optional[List[int]] = None

    class Config:
        from_attributes = True

class ProductUpdate(BaseModel):
    title : str | None = None
    description : str | None = None
    price : float | None = None
    stock_quantity : int | None = None
    image_url : str | None = None
    category_ids: list[int] | None = None
    model_config = {
        "from_attributes": True
    }