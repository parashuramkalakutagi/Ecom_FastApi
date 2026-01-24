
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, cast, or_
from typing import List
from datetime import datetime
from sqlalchemy.orm import selectinload
from fastapi import Query,status
from sqlalchemy import select, func, and_
from app.core.jwt_auth import require_admin, verify_jwt_token
from app.db.config import get_session
from app.models import User, Shipping_Status, Product
from app.models.order import Order, OrderStatus,OrderItem
from app.models.payment import PaymentModel,PaymentGateway,PaymentStatus
from app.models.payment import PaymentGateway as PaymentGatewayEnum
from app.schemas.cart import *
from app.schemas.orders import OrderResponse
from app.schemas.payment import PaymentCreate, PaymentOut
from app.models.cart import Cart_Item
from app.models.shipping_model import ShippingModel, ShippingStatus
from app.utils.mock_ids import generate_random_mock_id

router = APIRouter(prefix="/v1/payment", tags=["payment_gateway"])


async def create_payment(
        db_session: AsyncSession,
        user_id: int,
        data: PaymentCreate,
        order_id: int,
):
    address = await db_session.get(ShippingModel,data.shipping_address_id)
    if not address or address.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="invalid shipping address")

    gateway = PaymentGatewayEnum(data.gateway)
    if gateway == PaymentGateway.mock:
        is_sucess = data.simulate_success
        statuss = PaymentStatus.SUCCESS if is_sucess else PaymentStatus.FAILED
        pg_order_id,pg_payment_id,pg_signature = generate_random_mock_id()

        payment = PaymentModel(
            user_id = user_id,
            status = statuss,
            order_id=order_id,
            amount=data.amount,
            payment_gateway = gateway,
            is_paid = (statuss == PaymentStatus.SUCCESS ),
            payment_gateway_order_id = pg_order_id,
            payment_gateway_signature = pg_signature,
            payment_gateway_id = pg_payment_id,

        )
        db_session.add(payment)
        await db_session.commit()
        await db_session.refresh(payment)
        return payment


    elif gateway == PaymentGatewayEnum.razorpay:
        pass
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="invalid gateway")



@router.post("/checkout",response_model=OrderResponse,status_code=status.HTTP_201_CREATED)
async def checkout(
        payment_data: PaymentCreate,
        user: User = Depends(verify_jwt_token),
        session: AsyncSession = Depends(get_session)
) -> Order:
    # Fetch all cart items for the user, locking rows for update (to prevent race conditions)
    user_id = user["user_id"]
    stmt = select(Cart_Item).where(Cart_Item.user_id == user_id).options(selectinload(Cart_Item.product)).with_for_update()

    result = await session.execute(stmt)
    cart_items = result.scalars().all()

    # If no items found, cart is empty → checkout not possible
    if not cart_items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    # Track total cost
    total_price = Decimal("0.0")
    # Will store OrderItem instances for bulk add
    order_items: list[OrderItem] = []

    # Validate each cart item
    for item in cart_items:
        if not item.product:
            # Skip if product no longer exists (rare case)
            continue

        # Check stock availability
        if item.product.stock_quantity < item.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Insufficient stock")

        # Ensure price consistency (prevents price manipulation on frontend)
        if item.product.price != item.price:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Price mismatch")

        # Add to total price (Decimal used to prevent floating point errors)
        total_price += Decimal(str(item.price)) * item.quantity

        # Prepare OrderItem entry for this product
        order_items.append(OrderItem(
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
        ))

    # Check that payment amount matches cart total (allowing 0.01 difference due to float precision)
    if abs(total_price - Decimal(str(payment_data.amount))) > Decimal("0.01"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment amount does not match cart total")

    # Validate shipping address
    address = await session.get(ShippingModel, payment_data.shipping_address_id)
    if not address or address.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid shipping address")

    # Create new Order (status will be updated after payment success)
    order = Order(
        user_id=user_id,
        total_price=float(total_price),
        shipping_address_id=payment_data.shipping_address_id
    )
    session.add(order)
    # Ensure order.id is generated before creating payment
    await session.flush()

    # Process payment
    payment = await create_payment(
        db_session=session,
        data=payment_data,
        user_id=user_id,
        order_id=order.id
    )

    # If payment fails, rollback transaction and abort checkout
    if not payment.is_paid:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment failed")

    # Update order status to confirmed after payment
    order.status = OrderStatus.confirmed
    session.add(order)

    # Create shipping status entry (starts as pending)
    shipping_status = Shipping_Status(
        order_id=order.id,
        status=ShippingStatus.pending
    )
    session.add(shipping_status)

    # Add order items to DB and update product stock
    for oi in order_items:
        oi.order_id = order.id
        session.add(oi)
        # Reduce stock quantity for each product
        product = await session.get(Product, oi.product_id)
        if product:
            product.stock_quantity -= oi.quantity

    # Clear the user's cart
    for item in cart_items:
        await session.delete(item)

    # Commit all changes to the database
    await session.commit()
    await session.refresh(order)

    # # Fetch the order again with related entities (items, address, shipping)
    # stmt = (
    #     select(Order)
    #     .where(Order.id == order.id)
    #     .options(
    #         selectinload(Order.order_item),
    #         selectinload(Order.shipping_model),
    #         selectinload(Order.Shipping_Status),
    #     )
    # )

    stmt = await session.execute(
        select(Order)
        .where(Order.id == order.id)
        .options(
            selectinload(Order.order_item),
            selectinload(Order.shipping_model),
            selectinload(Order.Shipping_Status),
        )
    )


    return stmt.scalar_one()


@router.get("/payments/{order_id}", response_model=PaymentOut)
async def get_payment_by_order_id(
    order_id: int,
    session: AsyncSession = Depends(get_session),
    user:User = Depends(verify_jwt_token),
):
  user_id = user["user_id"]
  stmt = select(PaymentModel).where(PaymentModel.order_id == order_id, PaymentModel.user_id == user_id)
  result = await session.execute(stmt)
  return result.scalar_one_or_none()


@router.get("/", response_model=list[PaymentOut])
async def list_payments_by_user(session: AsyncSession = Depends(get_session)
                                , user: User = Depends(verify_jwt_token)):
  user_id = user["user_id"]
  stmt = select(PaymentModel).where(PaymentModel.user_id == user_id)
  result = await session.execute(stmt)
  return result.scalars().all()