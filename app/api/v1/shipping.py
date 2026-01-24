
from fastapi import APIRouter, Depends, HTTPException

from app.models.order import OrderStatus
from app.schemas.orders import OrderResponse
from app.schemas.shipping import ShippingBase, ShippingCreate, ShippingResponse, DeleteResponse, ShippingStatusCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, cast, or_
from typing import List
from datetime import datetime
from slugify import slugify
from sqlalchemy.orm import selectinload
from fastapi import Query
from sqlalchemy import select, func, and_
from app.core.jwt_auth import require_admin, verify_jwt_token
from app.db.config import get_session
from app.models import User, Order
from app.models.shipping_model import ShippingModel, ShippingStatus

router = APIRouter(prefix="/v1/shipping", tags=["shipping"])


@router.post("/address", response_model=ShippingResponse)
async def create_shipping(
        data: ShippingCreate,
        db: AsyncSession = Depends(get_session),
        user: dict = Depends(verify_jwt_token),
):
    user_id = user["user_id"]

    if not user_id:
        raise HTTPException(status_code=400, detail="User does not exist")

    shipping = ShippingModel(
        user_id=user_id,
        name=data.name,
        address=data.address,
        city=data.city,
        state=data.state,
        email=data.email,
        phone=data.phone,

    )
    db.add(shipping)
    await  db.commit()
    await  db.refresh(shipping)
    return shipping


@router.get("/address", response_model=List[ShippingResponse])
async def get_shipping(
        db: AsyncSession = Depends(get_session),
        user: dict = Depends(verify_jwt_token),
):
    user_id = user["user_id"]
    if not user_id:
        raise HTTPException(status_code=400, detail="User does not exist")
    shipping = await db.execute(select(ShippingModel).where(ShippingModel.user_id == user_id))
    result = shipping.scalars().all()
    return result


@router.get("/address/{ids}", response_model=ShippingResponse)
async def get_shipping_address(
        ids: int,
        db: AsyncSession = Depends(get_session),
        user: dict = Depends(verify_jwt_token),
):
    user_id = user["user_id"]
    if not user_id:
        raise HTTPException(status_code=400, detail="User does not exist")
    shipping = await db.execute(select(ShippingModel).where(ShippingModel.user_id == user_id)
                                .where(ShippingModel.id == ids))
    result = shipping.scalars().one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail="Shipping address not found")

    return result

@router.put("/address/{ids}", response_model=ShippingResponse)
async def update_shipping(
        ids: int,
        data: ShippingCreate,
        db: AsyncSession = Depends(get_session),
        user: dict = Depends(verify_jwt_token),
):
    user_id = user["user_id"]
    if not user_id:
        raise HTTPException(status_code=400, detail="User does not exist")
    shipping = await db.execute(
        select(ShippingModel).where(ShippingModel.user_id == user_id)
        .where(ShippingModel.id == ids)
    )
    shipping = shipping.scalars().one_or_none()
    if not shipping:
        raise HTTPException(status_code=404, detail="Shipping address not found")

    shipping.name = data.name
    shipping.address = data.address
    shipping.city = data.city
    shipping.state = data.state
    shipping.email = data.email
    shipping.phone = data.phone
    await db.commit()
    await db.refresh(shipping)
    return shipping

@router.delete("/address/{ids}", response_model=DeleteResponse)
async def delete_shipping(
        ids: int,
        db: AsyncSession = Depends(get_session),
        user: dict = Depends(verify_jwt_token),
):
    user_id = user["user_id"]
    if not user_id:
        raise HTTPException(status_code=400, detail="User does not exist")
    shipping = await db.execute(
        select(ShippingModel).where(ShippingModel.user_id == user_id)
        .where(ShippingModel.id == ids)
    )
    shipping = shipping.scalars().one_or_none()
    if not shipping:
        raise HTTPException(status_code=404, detail="Shipping address not found")

    await db.delete(shipping)
    await db.commit()
    await db.refresh(shipping)
    return {"msg": "Shipping address deleted"}


@router.patch("/status/{oder_id}",response_model=OrderResponse)
async def update_shipping_status(
        oder_id:int,
        shipping_status: ShippingStatusCreate,
        db:AsyncSession = Depends(get_session),
        user: User = Depends(require_admin),
):

    stmt = await  db.execute(
        select(Order)
        .where(Order.id== oder_id)
        .options(
            selectinload(Order.order_item),
            selectinload(Order.shipping_model),
            selectinload(Order.Shipping_Status)

        )
    )
    order = stmt.scalars().one_or_none()
    if not order:
        raise HTTPException(status_code=400, detail="order does not exist")

    order.Shipping_Status.status = shipping_status.status
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order