from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from h11 import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, cast, or_
from typing import List
from datetime import datetime
from slugify import slugify
from sqlalchemy.orm import selectinload
from fastapi import Query
from sqlalchemy import select, func, and_
from app.core.image_upload import save_product_image
from app.core.jwt_auth import require_admin, verify_jwt_token
from app.db.config import get_session
from app.models import User
from app.models.product import Product, ProductCategory,Category
from app.models.cart import Cart_Item
from app.schemas.cart import *


router = APIRouter(prefix="/v1/cart", tags=["Cart"])

@router.get("/", response_model=CartResponse)
async def get_cart(
        db: AsyncSession = Depends(get_session),
        user: dict = Depends(verify_jwt_token),
):

    user_id = user["user_id"]

    # Load all cart items for this user
    result = await db.execute(
        select(Cart_Item)
        .where(Cart_Item.user_id == user_id)
        .options(selectinload(Cart_Item.product))
    )
    items = list(result.scalars().all())

    if not items:
        raise HTTPException(404, "Cart is empty")

    total_price = sum(item.price for item in items)

    return CartResponse(
        id=user_id,     # cart id = user id
        user_id=user_id,
        total_price=total_price,
        items=items
    )



@router.post("/", response_model=CartResponse)
async def add_to_cart(
        data: cart_Item_base,
        db: AsyncSession = Depends(get_session),
        user: dict = Depends(verify_jwt_token),
):

    user_id = user["user_id"]

    # 1️ Product exists?
    product = (await db.execute(
        select(Product).where(Product.id == data.product)
    )).scalar_one_or_none()

    if not product:
        raise HTTPException(404, "Product not found")

    # 2️Item already in user's cart?
    existing_item = (await db.execute(
        select(Cart_Item)
        .where(Cart_Item.user_id == user_id)
        .where(Cart_Item.product_id == data.product)
    )).scalar_one_or_none()

    if existing_item:
        existing_item.quantity += data.quantity
        existing_item.price = existing_item.quantity * product.price
    else:
        new_item = Cart_Item(
            user_id=user_id,
            product_id=product.id,
            quantity=data.quantity,
            price=product.price * data.quantity
        )
        db.add(new_item)

    await db.commit()

    # 3️Load all cart items for this user
    result = await db.execute(
        select(Cart_Item)
        .where(Cart_Item.user_id == user_id)
        .options(selectinload(Cart_Item.product))
    )
    items = list(result.scalars().all())

    total_price = sum(item.price for item in items)

    return CartResponse(
        id=user_id,            # cart id = user id
        user_id=user_id,
        total_price=total_price,
        items=items
    )
@router.delete("/{product_id}", response_model=CartResponse)
async def delete_from_cart(
        product_id: int,
        db: AsyncSession = Depends(get_session),
        user: dict = Depends(verify_jwt_token)
):

    user_id = user["user_id"]

    # 1️ Check if item exists in this user's cart
    cart_item = (await db.execute(
        select(Cart_Item)
        .where(Cart_Item.user_id == user_id)
        .where(Cart_Item.product_id == product_id)
    )).scalar_one_or_none()

    if not cart_item:
        raise HTTPException(404, "Product not found in your cart")

    # 2️ Delete this cart item
    await db.delete(cart_item)
    await db.commit()

    # 3️ Load updated cart items
    result = await db.execute(
        select(Cart_Item)
        .where(Cart_Item.user_id == user_id)
        .options(selectinload(Cart_Item.product))
    )
    items = list(result.scalars().all())

    if not items:
        # Cart becomes empty
        return CartResponse(
            id=user_id,
            user_id=user_id,
            total_price=0.0,
            items=[]
        )

    # 4️ Recalculate total price
    total_price = sum(item.price for item in items)

    # 5️ Return updated cart
    return CartResponse(
        id=user_id,
        user_id=user_id,
        total_price=total_price,
        items=items
    )
