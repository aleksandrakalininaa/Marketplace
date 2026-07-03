"""
Бизнес-логика каталога: получение дерева категорий, поиск товаров с фильтрами.
"""
import uuid
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.catalog import Category, CatalogProduct


async def get_category_tree(db: AsyncSession) -> list[Category]:
    """Возвращает корневые категории с рекурсивно загруженными дочерними."""
    result = await db.execute(
        select(Category)
        .where(Category.parent_id.is_(None))
        .options(selectinload(Category.children).selectinload(Category.children))
        .order_by(Category.name)
    )
    return list(result.scalars().all())


async def _get_descendant_category_ids(
    db: AsyncSession, category_id: uuid.UUID
) -> list[uuid.UUID]:
    """Рекурсивно собирает ID категории и всех её потомков."""
    ids = [category_id]
    result = await db.execute(
        select(Category)
        .where(Category.parent_id == category_id)
        .options(selectinload(Category.children))
    )
    children = result.scalars().all()
    for child in children:
        ids.extend(await _get_descendant_category_ids(db, child.id))
    return ids


async def get_products(
    db: AsyncSession,
    search: str,
    category_id: Optional[uuid.UUID] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    sort: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
):
    """
    Поиск товаров с фильтрацией, сортировкой и пагинацией.
    search — обязательный поисковый запрос (ILIKE по name и description).
    category_id — опциональный фильтр по категории и подкатегориям.
    """
    # Базовый запрос: только активные товары
    query = select(CatalogProduct).where(CatalogProduct.is_active == True)

    # Поисковый запрос
    if search:
        like_pattern = f"%{search}%"
        query = query.where(
            CatalogProduct.name.ilike(like_pattern)
            | CatalogProduct.description.ilike(like_pattern)
        )

    # Фильтр по категории
    if category_id is not None:
        category_ids = await _get_descendant_category_ids(db, category_id)
        query = query.where(CatalogProduct.category_id.in_(category_ids))

    # Фильтр по наличию
    if in_stock:
        query = query.where(CatalogProduct.quantity > 0)

    # Фильтр по цене
    if min_price is not None:
        query = query.where(CatalogProduct.price >= min_price)

    if max_price is not None:
        query = query.where(CatalogProduct.price <= max_price)

    # Подсчёт общего количества
    count_query = select(func.count()).select_from(
        select(CatalogProduct.id).where(*query.whereclause).subquery()
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Сортировка
    sort_map = {
        "price_asc": CatalogProduct.price.asc(),
        "price_desc": CatalogProduct.price.desc(),
        "name_asc": CatalogProduct.name.asc(),
        "name_desc": CatalogProduct.name.desc(),
        "newest": CatalogProduct.created_at.desc(),
    }
    order_by = sort_map.get(sort, CatalogProduct.created_at.desc())
    query = query.order_by(order_by)

    # Пагинация
    offset = (page - 1) * limit
    query = query.options(selectinload(CatalogProduct.category)).offset(offset).limit(limit)

    result = await db.execute(query)
    items = list(result.scalars().all())

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
    }