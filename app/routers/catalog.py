"""
Роутер каталога: категории и товары.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.catalog import CatalogProduct
from app.schemas.catalog import CategoryOut, ProductDetail, ProductListResponse
from app.services.catalog import get_category_tree, get_products

router = APIRouter(prefix="/api/v1", tags=["catalog"])


@router.get(
    "/categories",
    response_model=list[CategoryOut],
    responses={500: {"description": "Ошибка сервера"}},
)
async def list_categories(db: AsyncSession = Depends(get_db)):
    """Возвращает дерево категорий (корневые + дочерние рекурсивно)."""
    try:
        categories = await get_category_tree(db)
        return categories
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "internal_error", "message": str(e)},
        )


@router.get(
    "/products",
    response_model=ProductListResponse,
    responses={
        400: {"description": "Некорректные параметры"},
        500: {"description": "Ошибка сервера"},
    },
)
async def list_products(
    category_id: uuid.UUID = Query(..., description="ID категории"),
    min_price: float | None = Query(None, ge=0, description="Минимальная цена"),
    max_price: float | None = Query(None, ge=0, description="Максимальная цена"),
    in_stock: bool | None = Query(None, description="Только в наличии"),
    sort: str | None = Query(
        None,
        description="Сортировка: price_asc, price_desc, name_asc, name_desc, newest",
    ),
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(20, ge=1, le=50, description="Элементов на странице"),
    db: AsyncSession = Depends(get_db),
):
    """Возвращает список товаров в категории с фильтрацией и пагинацией."""
    allowed_sorts = {"price_asc", "price_desc", "name_asc", "name_desc", "newest"}
    if sort is not None and sort not in allowed_sorts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_sort",
                "message": f"sort должен быть одним из: {', '.join(allowed_sorts)}",
            },
        )
    try:
        result = await get_products(
            db=db,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            in_stock=in_stock,
            sort=sort,
            page=page,
            limit=limit,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "internal_error", "message": str(e)},
        )


@router.get(
    "/products/{product_id}",
    response_model=ProductDetail,
    responses={
        404: {"description": "Товар не найден"},
        500: {"description": "Ошибка сервера"},
    },
)
async def get_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Возвращает полную информацию о товаре по ID."""
    try:
        result = await db.execute(
            select(CatalogProduct)
            .where(CatalogProduct.id == product_id)
            .options(selectinload(CatalogProduct.category))
        )
        product = result.scalar_one_or_none()
        if product is None or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "not_found", "message": "Товар не найден"},
            )
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "internal_error", "message": str(e)},
        )