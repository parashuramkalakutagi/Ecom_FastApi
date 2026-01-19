import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum
from starlette import status

class cart_Item_base(BaseModel):
    product_id: int
    quantity: int
    price: float

class cart_response(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    user_id: int

    class Config:
        from_attributes = True


