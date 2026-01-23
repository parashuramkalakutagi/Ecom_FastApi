from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


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