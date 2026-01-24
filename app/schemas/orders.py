from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.shipping import ShippingStatusResponse, ShippingResponse


class OrderedProductInfo(BaseModel):
    title: str
    description: str
    model_config = {"from_attributes": True}


class OrderItemOut(BaseModel):
    id: int
    product_id: int | None
    quantity: int
    price: float
    product: OrderedProductInfo | None
    model_config = {"from_attributes": True}

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    created_at: datetime

    # match SQLAlchemy relationship names exactly
    shipping_address: ShippingResponse = Field(alias="shipping_model")
    shipping_status: Optional[ShippingStatusResponse ]= Field(alias="Shipping_Status")
    items: List[OrderItemOut] = Field(alias="order_item")

    class Config:
        from_attributes = True
        populate_by_name = True





