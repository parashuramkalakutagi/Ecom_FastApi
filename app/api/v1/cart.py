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
from app.schemas.cart import cart_response,cart_Item_base


router = APIRouter(prefix="/v1/cart", tags=["Cart"])

@router.post("/", response_model=cart_response, status_code=status.HTTP_201_CREATED)
async def create_cart(
        data: cart_Item_base,
        db:AsyncSession = Depends(get_session),
        user:User = Depends(verify_jwt_token),
):

    user_id = user["user_id"]
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

    result = await db.execute(select(Product).where(Product.id == data.product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found")

    result = await db.execute(select(Cart_Item).where(Cart_Item.product_id== data.product_id))
    cart_item = result.scalar_one_or_none()

    if cart_item:
       raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Item already exists")

    cart = Cart_Item(
        user_id=user.id,
        product_id=product.id,
        quantity=data.quantity,
        price=round(data.price * data.quantity, 2),
    )
    db.add(cart)
    await db.commit()
    await db.refresh(cart)
    return cart