import enum
from datetime import datetime
from typing import Optional, List

from typing import Literal
from pydantic import BaseModel, Field

from app.models import ShippingStatus


class ShippingBase(BaseModel):
    name: str
    address: str
    city: str
    state: str
    phone: str
    email: str

class ShippingCreate(ShippingBase):
    pass

class ShippingResponse(ShippingBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class DeleteResponse(ShippingBase):
    msg:str

    class Config:
        from_attributes = True

class ShippingStatusResponse(BaseModel):
    id: int
    order_id: int
    status: ShippingStatus
    update_at: datetime


    class Config:
        from_attributes = True

class ShippingStatusCreate(BaseModel):
    status:Literal["pending","processing","shipped","delevered","cancelled"] = Field(default="processing")
