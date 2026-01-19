from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, cast
from typing import List
from datetime import datetime

from sqlalchemy.orm import selectinload
from fastapi import Query

from app.core.image_upload import save_product_image
from app.core.jwt_auth import require_admin
from app.db.config import get_session
from app.models import User
from app.models.product import Product, ProductCategory,Category
from app.schemas.products import ProductCreate, ProductResponse, CategoryResponse, CategoryCreate, CategoryResponses

router = APIRouter(prefix="/v1/products", tags=["Products"])


async def get_categories_by_ids(db: AsyncSession, ids: List[int]):
    if not ids:
        return []

    result = await db.execute(
        select(Category).where(Category.id.in_(ids))
    )
    categories = result.scalars().all()

    if len(categories) != len(ids):
        raise HTTPException(
            status_code=404,
            detail="One or more category IDs do not exist"
        )
    return categories


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_product(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    slug: str = Form(...),
    stock_quantity: int = Form(...),
    category_ids: List[int] | None = Query(None),
    image: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_session),
    admin:User = Depends(require_admin)
):
    # Build Pydantic model
    product_data = ProductCreate(
        title=title,
        description=description,
        price=price,
        slug=slug,
        stock_quantity=stock_quantity,
        category_ids=category_ids
    )

    # Save image
    image_path = await save_product_image(image) if image else None

    # Fetch categories properly
    categories = await get_categories_by_ids(
        db=db,
        ids=product_data.category_ids or []
    )

    # Create Product
    product = Product(
        title=product_data.title,
        description=product_data.description,
        image=image_path,
        price=product_data.price,
        slug=product_data.slug,
        stock_quantity=product_data.stock_quantity
    )

    product.categories = categories

    db.add(product)
    await db.commit()
    await db.refresh(product)

    return product




@router.get("/", response_model=List[ProductResponse])
async def get_all_products(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Product))
    return result.scalars().all()




@router.post("/category", response_model=CategoryResponse)
async def create_product_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_session),
    admin:User = Depends(require_admin)
):
    category = Category(
        name=category_data.name,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category

#
@router.get("/categories_all", response_model=list[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Category))
    return result.scalars().all()


@router.get("/categories", response_model=list[CategoryResponses])
async def get_categories(db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(Category).options(selectinload(Category.products))
    )

    categories = result.scalars().all()
    return categories


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_session),):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(404, "Product not found")
    return product