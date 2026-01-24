from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, and_
from app.core.jwt_auth import require_admin, verify_jwt_token
from app.db.config import get_session
from app.models import User
from app.models.order import Order,OrderStatus
from app.models.shipping_model import ShippingModel,ShippingStatus
from app.schemas.cart import *
from app.schemas.orders import OrderResponse



router = APIRouter(prefix="/v1/order", tags=["order"])

@router.get("/",response_model=List[OrderResponse])
async def get_order_for_user(
        db:AsyncSession = Depends(get_session),
        user: User = Depends(verify_jwt_token),
):
    user_id = user["user_id"]
    stmt = await  db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .options(
            selectinload(Order.order_item),
            selectinload(Order.shipping_model),
            selectinload(Order.Shipping_Status)

        )
    )
    result = stmt.scalars().all()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found")
    return result


@router.get("/{oder_id}",response_model=OrderResponse)
async def get_order_for_user(
        oder_id:int,
        db:AsyncSession = Depends(get_session),
        user: User = Depends(verify_jwt_token),
):
    user_id = user["user_id"]
    stmt = await  db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .where(Order.id== oder_id)
        .options(
            selectinload(Order.order_item),
            selectinload(Order.shipping_model),
            selectinload(Order.Shipping_Status)

        )
    )
    result = stmt.scalars().one_or_none()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found")
    return result



@router.patch("/cancel/{oder_id}",response_model=OrderResponse)
async def cancel_order_for_user(
        oder_id:int,
        db:AsyncSession = Depends(get_session),
        user: User = Depends(verify_jwt_token),
):
    user_id = user["user_id"]
    stmt = await  db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .where(Order.id== oder_id)
        .options(
            selectinload(Order.order_item),
            selectinload(Order.shipping_model),
            selectinload(Order.Shipping_Status)

        )
    )
    order = stmt.scalars().one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found")

    order.status = OrderStatus.cancelled
    order.Shipping_Status.status = ShippingStatus.cancelled
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


@router.patch("/cancel/{oder_id}",response_model=OrderResponse)
async def update_shipping_status(
        oder_id:int,
        db:AsyncSession = Depends(get_session),
        user: User = Depends(verify_jwt_token),
):
    user_id = user["user_id"]
    stmt = await  db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .where(Order.id== oder_id)
        .options(
            selectinload(Order.order_item),
            selectinload(Order.shipping_model),
            selectinload(Order.Shipping_Status)

        )
    )
    order = stmt.scalars().one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found")

    order.status = OrderStatus.cancelled
    order.Shipping_Status.status = ShippingStatus.cancelled
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order