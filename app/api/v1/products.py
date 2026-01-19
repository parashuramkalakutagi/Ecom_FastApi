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
from app.core.jwt_auth import require_admin
from app.db.config import get_session
from app.models import User
from app.models.product import Product, ProductCategory,Category
from app.schemas.products import ProductCreate, ProductResponse, CategoryResponse, CategoryCreate, CategoryResponses, \
    DeleteResponse, PaginatedProductResponse, ProductUpdate, ProductPatch

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
        slug=slugify(title),
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


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK
)
async def update_product(
    product_id: int,
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    category_ids: List[int] | None = Query(None),
    image: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_session),
    admin: User = Depends(require_admin)
):
    # Fetch product
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Fetch categories
    categories = await get_categories_by_ids(
        db=db,
        ids=category_ids or []
    )

    # Save image if provided
    if image:
        product.image = await save_product_image(image)

    # Update fields
    product.title = title
    product.description = description
    product.price = price
    product.stock_quantity = stock_quantity

    # Update slug only if title changed
    if product.slug != slugify(title):
        product.slug = slugify(title)

    # Update categories (M2M)
    product.categories = categories

    await db.commit()
    await db.refresh(product)

    return product


@router.get("/", response_model=PaginatedProductResponse)
async def get_all_products(
    skip: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_session),
):
    offset = (skip - 1) * limit

    total_result = await db.execute(
        select(func.count()).select_from(Product)
    )
    total = total_result.scalar_one()

    result = await db.execute(
        select(Product)
        .offset(offset)
        .limit(limit)
    )

    products = result.scalars().all()

    return {
        "total": total,
        "page": skip,
        "limit": limit,
        "items": products,
    }











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
async def get_categories(db: AsyncSession = Depends(get_session),admin:User = Depends(require_admin)):
    result = await db.execute(select(Category))
    return result.scalars().all()


@router.get("/categories", response_model=list[CategoryResponses])
async def get_categories(db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(Category).options(selectinload(Category.products))
    )
    categories = result.scalars().all()
    return categories




@router.get("/search", response_model=list[ProductResponse])
async def search_products(
    q: str | None = Query(None, description="Search by title, description, slug"),
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_session),
):
    offset = (page - 1) * size

    stmt = select(Product).options(selectinload(Product.categories))

    filters = []

    #TEXT SEARCH (case-insensitive LIKE)
    if q:
        pattern = f"%{q.lower()}%"
        filters.append(
            or_(
                func.lower(Product.title).like(pattern),
                func.lower(Product.description).like(pattern),
                func.lower(Product.slug).like(pattern)
            )
        )

    # MIN PRICE
    if min_price is not None:
        filters.append(Product.price >= min_price)

    # MAX PRICE
    if max_price is not None:
        filters.append(Product.price <= max_price)

    if filters:
        stmt = stmt.where(and_(*filters))

    # pagination
    stmt = stmt.limit(size).offset(offset)

    result = await db.execute(stmt)
    products = result.scalars().all()

    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_session),):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(404, "Product not found")
    return product


@router.get("/slug/{slug}", response_model=ProductResponse)
async def get_product(slug: str, db: AsyncSession = Depends(get_session),):
    result = await db.execute(select(Product).where(Product.slug == slug))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(404, "Product not found")
    return product



@router.delete("/category/{category_id}", response_model=DeleteResponse, status_code=200)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_session),
    admin: User = Depends(require_admin)
):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(404, "Category not found")

    await db.delete(category)
    await db.commit()

    return {"msg": "Category deleted successfully"}


@router.delete("/{product_id}", response_model=DeleteResponse, status_code=200)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_session), admin: User = Depends(require_admin)):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    await db.delete(product)
    await db.commit()
    return {"msg": "Product deleted successfully"}