"""
Скрипт наполнения БД тестовыми категориями и товарами.
Запуск: python scripts/seed_catalog.py
"""
import asyncio
import uuid
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.catalog import Category, CatalogProduct


CATEGORIES = [
    {"name": "Электроника", "slug": "electronics", "children": [
        {"name": "Смартфоны", "slug": "smartphones"},
        {"name": "Ноутбуки", "slug": "laptops"},
        {"name": "Наушники", "slug": "headphones"},
        {"name": "Планшеты", "slug": "tablets"},
    ]},
    {"name": "Одежда", "slug": "clothing", "children": [
        {"name": "Мужская одежда", "slug": "mens-clothing"},
        {"name": "Женская одежда", "slug": "womens-clothing"},
        {"name": "Обувь", "slug": "shoes"},
    ]},
    {"name": "Дом и сад", "slug": "home-garden", "children": [
        {"name": "Мебель", "slug": "furniture"},
        {"name": "Освещение", "slug": "lighting"},
        {"name": "Декор", "slug": "decor"},
    ]},
    {"name": "Спорт и отдых", "slug": "sport", "children": [
        {"name": "Фитнес", "slug": "fitness"},
        {"name": "Велоспорт", "slug": "cycling"},
        {"name": "Туризм", "slug": "tourism"},
    ]},
]


def _product(name: str, price: float, quantity: int, image_urls: list[str] | None = None):
    return {"name": name, "description": f"Отличный товар: {name}", "price": price, "quantity": quantity, "image_urls": image_urls or []}


PRODUCTS_BY_SLUG = {
    "smartphones": [
        _product("iPhone 15 Pro", 129990, 15, ["https://picsum.photos/seed/iphone15/400/400"]),
        _product("Samsung Galaxy S24", 109990, 20, ["https://picsum.photos/seed/s24/400/400"]),
        _product("Xiaomi 14 Pro", 69990, 30, ["https://picsum.photos/seed/xiaomi14/400/400"]),
        _product("Google Pixel 8", 79990, 10, ["https://picsum.photos/seed/pixel8/400/400"]),
        _product("OnePlus 12", 89990, 8, ["https://picsum.photos/seed/op12/400/400"]),
    ],
    "laptops": [
        _product("MacBook Pro 16 M3", 249990, 5, ["https://picsum.photos/seed/mbp16/400/400"]),
        _product("Dell XPS 15", 189990, 7, ["https://picsum.photos/seed/xps15/400/400"]),
        _product("Lenovo ThinkPad X1", 169990, 12, ["https://picsum.photos/seed/x1/400/400"]),
        _product("ASUS ROG Zephyrus", 219990, 3, ["https://picsum.photos/seed/rog/400/400"]),
    ],
    "headphones": [
        _product("AirPods Pro 2", 24990, 40, ["https://picsum.photos/seed/airpods/400/400"]),
        _product("Sony WH-1000XM5", 34990, 25, ["https://picsum.photos/seed/sonyxm5/400/400"]),
        _product("Bose QC45", 29990, 18, ["https://picsum.photos/seed/bose/400/400"]),
        _product("JBL Tune 770", 7990, 60, ["https://picsum.photos/seed/jbl/400/400"]),
    ],
    "tablets": [
        _product("iPad Air M2", 79990, 14, ["https://picsum.photos/seed/ipadair/400/400"]),
        _product("Samsung Tab S9", 69990, 10, ["https://picsum.photos/seed/tabs9/400/400"]),
        _product("Xiaomi Pad 6", 34990, 22, ["https://picsum.photos/seed/xpad6/400/400"]),
    ],
    "mens-clothing": [
        _product("Куртка кожаная", 15990, 20, ["https://picsum.photos/seed/jacket/400/400"]),
        _product("Джинсы классические", 6990, 35, ["https://picsum.photos/seed/jeans/400/400"]),
        _product("Футболка хлопок", 1990, 100, ["https://picsum.photos/seed/tshirt/400/400"]),
        _product("Свитер шерстяной", 8990, 15, ["https://picsum.photos/seed/sweater/400/400"]),
    ],
    "womens-clothing": [
        _product("Платье вечернее", 12990, 12, ["https://picsum.photos/seed/dress/400/400"]),
        _product("Блузка шёлковая", 5990, 25, ["https://picsum.photos/seed/blouse/400/400"]),
        _product("Юбка-карандаш", 4990, 30, ["https://picsum.photos/seed/skirt/400/400"]),
    ],
    "shoes": [
        _product("Кроссовки Nike Air", 12990, 40, ["https://picsum.photos/seed/nike/400/400"]),
        _product("Ботинки Timberland", 18990, 15, ["https://picsum.photos/seed/timber/400/400"]),
        _product("Туфли классические", 9990, 20, ["https://picsum.photos/seed/shoes/400/400"]),
    ],
    "furniture": [
        _product("Диван угловой", 89990, 3, ["https://picsum.photos/seed/sofa/400/400"]),
        _product("Стол обеденный", 24990, 8, ["https://picsum.photos/seed/table/400/400"]),
        _product("Стул офисный", 15990, 20, ["https://picsum.photos/seed/chair/400/400"]),
        _product("Кровать двуспальная", 54990, 4, ["https://picsum.photos/seed/bed/400/400"]),
    ],
    "lighting": [
        _product("Люстра хрустальная", 34990, 6, ["https://picsum.photos/seed/lustre/400/400"]),
        _product("Торшер напольный", 7990, 15, ["https://picsum.photos/seed/lamp/400/400"]),
        _product("Светильник LED", 2990, 50, ["https://picsum.photos/seed/led/400/400"]),
    ],
    "decor": [
        _product("Картина маслом", 19990, 5, ["https://picsum.photos/seed/paint/400/400"]),
        _product("Ваза керамическая", 4990, 18, ["https://picsum.photos/seed/vase/400/400"]),
        _product("Зеркало настенное", 8990, 10, ["https://picsum.photos/seed/mirror/400/400"]),
    ],
    "fitness": [
        _product("Гантели 10 кг", 4990, 30, ["https://picsum.photos/seed/dumb/400/400"]),
        _product("Коврик для йоги", 2990, 45, ["https://picsum.photos/seed/yoga/400/400"]),
        _product("Скакалка", 990, 80, ["https://picsum.photos/seed/rope/400/400"]),
        _product("Фитбол", 1990, 25, ["https://picsum.photos/seed/fitball/400/400"]),
    ],
    "cycling": [
        _product("Велосипед горный", 59990, 5, ["https://picsum.photos/seed/bike/400/400"]),
        _product("Шлем велосипедный", 4990, 20, ["https://picsum.photos/seed/helmet/400/400"]),
        _product("Вело-перчатки", 1490, 35, ["https://picsum.photos/seed/gloves/400/400"]),
    ],
    "tourism": [
        _product("Палатка 3-местная", 15990, 8, ["https://picsum.photos/seed/tent/400/400"]),
        _product("Спальник", 6990, 14, ["https://picsum.photos/seed/sleepbag/400/400"]),
        _product("Рюкзак 60л", 8990, 12, ["https://picsum.photos/seed/backpack/400/400"]),
    ],
}


async def seed():
    async with AsyncSessionLocal() as db:
        # Проверим, есть ли уже данные
        result = await db.execute(select(Category).limit(1))
        if result.scalar_one_or_none():
            print("База уже содержит данные. Пропускаем.")
            return

        # Создаём категории
        created: dict[str, uuid.UUID] = {}

        for cat_data in CATEGORIES:
            cat = Category(name=cat_data["name"], slug=cat_data["slug"])
            db.add(cat)
            await db.flush()
            created[cat.slug] = cat.id
            print(f"  + Категория: {cat.name}")

            for child_data in cat_data.get("children", []):
                child = Category(name=child_data["name"], slug=child_data["slug"], parent_id=cat.id)
                db.add(child)
                await db.flush()
                created[child.slug] = child.id
                print(f"    - Подкатегория: {child.name}")

        # Создаём товары
        total_products = 0
        for slug, products in PRODUCTS_BY_SLUG.items():
            cat_id = created.get(slug)
            if not cat_id:
                continue
            for p in products:
                product = CatalogProduct(
                    category_id=cat_id,
                    name=p["name"],
                    description=p["description"],
                    price=p["price"],
                    quantity=p["quantity"],
                    image_urls=p["image_urls"],
                )
                db.add(product)
                total_products += 1

        await db.commit()
        print(f"\n✔ Создано категорий: {len(created)}, товаров: {total_products}")


if __name__ == "__main__":
    asyncio.run(seed())