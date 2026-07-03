"""
Скрипт наполнения БД тестовыми категориями и товарами.
Запуск: python scripts/seed_catalog.py
"""
import asyncio
import uuid
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, delete
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

# Картинки с Unsplash (реальные фото товаров)
IMG = {
    "iphone": ["https://picsum.photos/photo-1510557880182-3d4d3cba35a5?w=400&h=400&fit=crop"],
    "samsung": ["https://picsum.photos/photo-1610945265064-0e34e5519bbf?w=400&h=400&fit=crop"],
    "xiaomi": ["https://picsum.photos/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop"],
    "pixel": ["https://picsum.photos/photo-1598327105666-5b89351aff97?w=400&h=400&fit=crop"],
    "oneplus": ["https://picsum.photos/photo-1546054454-aa26e2b734c7?w=400&h=400&fit=crop"],
    "macbook": ["https://picsum.photos/photo-1517336714731-489689fd1ca8?w=400&h=400&fit=crop"],
    "dell": ["https://picsum.photos/photo-1593642632823-8f785ba67e45?w=400&h=400&fit=crop"],
    "thinkpad": ["https://picsum.photos/photo-1588872657578-7efd1f1555ed?w=400&h=400&fit=crop"],
    "asus": ["https://picsum.photos/photo-1603302576837-37561b2e2302?w=400&h=400&fit=crop"],
    "airpods": ["https://picsum.photos/photo-1606841837239-c5a1a4a07af7?w=400&h=400&fit=crop"],
    "sony": ["https://picsum.photos/photo-1618366712010-f4ae9c647dcb?w=400&h=400&fit=crop"],
    "bose": ["https://picsum.photos/photo-1546435770-a3e426bf472b?w=400&h=400&fit=crop"],
    "jbl": ["https://picsum.photos/photo-1608043152269-423dbba4e7e1?w=400&h=400&fit=crop"],
    "ipad": ["https://picsum.photos/photo-1544244015-0df4b3ffc6b0?w=400&h=400&fit=crop"],
    "tab_s9": ["https://picsum.photos/photo-1585790050230-5dd28404ccb0?w=400&h=400&fit=crop"],
    "xpad": ["https://picsum.photos/photo-1561154464-82e9adf32764?w=400&h=400&fit=crop"],
    "jacket": ["https://picsum.photos/photo-1551028719-00167b16eac5?w=400&h=400&fit=crop"],
    "jeans": ["https://picsum.photos/photo-1542272454315-4c01d7abdf4a?w=400&h=400&fit=crop"],
    "tshirt": ["https://picsum.photos/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop"],
    "sweater": ["https://picsum.photos/photo-1620799140408-edc6dcb6d633?w=400&h=400&fit=crop"],
    "dress": ["https://picsum.photos/photo-1572804013309-59a88b7e92f1?w=400&h=400&fit=crop"],
    "blouse": ["https://picsum.photos/photo-1604336755604-96ee6fa9f3f1?w=400&h=400&fit=crop"],
    "skirt": ["https://picsum.photos/photo-1583496661160-fb5886a0aaaa?w=400&h=400&fit=crop"],
    "nike": ["https://picsum.photos/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop"],
    "timberland": ["https://picsum.photos/photo-1608256246200-53e635b5b65f?w=400&h=400&fit=crop"],
    "classic_shoes": ["https://picsum.photos/photo-1614252369475-531eba835eb1?w=400&h=400&fit=crop"],
    "sofa": ["https://picsum.photos/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop"],
    "table": ["https://picsum.photos/photo-1524758631624-e2822e304c36?w=400&h=400&fit=crop"],
    "chair": ["https://picsum.photos/photo-1592078615290-033ee584e267?w=400&h=400&fit=crop"],
    "bed": ["https://picsum.photos/photo-1505693416388-ac5ce068fe85?w=400&h=400&fit=crop"],
    "chandelier": ["https://picsum.photos/photo-1524484485831-a92ffc0de03f?w=400&h=400&fit=crop"],
    "floor_lamp": ["https://picsum.photos/photo-1507473885765-e6ed057ab6fe?w=400&h=400&fit=crop"],
    "led_light": ["https://picsum.photos/photo-1565814329452-e1efa11c5b89?w=400&h=400&fit=crop"],
    "painting": ["https://picsum.photos/photo-1579783902614-a3fb3927b6a5?w=400&h=400&fit=crop"],
    "vase": ["https://picsum.photos/photo-1581783898377-1c85bf937427?w=400&h=400&fit=crop"],
    "mirror": ["https://picsum.photos/photo-1618220252344-8ec99ec624b1?w=400&h=400&fit=crop"],
    "dumbbell": ["https://picsum.photos/photo-1638536532686-d610adfc8e5c?w=400&h=400&fit=crop"],
    "yoga_mat": ["https://picsum.photos/photo-1601925260368-ae2f83cf8b7f?w=400&h=400&fit=crop"],
    "rope": ["https://picsum.photos/photo-1598289431512-b97b0917affc?w=400&h=400&fit=crop"],
    "fitball": ["https://picsum.photos/photo-1518611012118-696072aa579a?w=400&h=400&fit=crop"],
    "bike": ["https://picsum.photos/photo-1485965120184-e220f721d03e?w=400&h=400&fit=crop"],
    "helmet": ["https://picsum.photos/photo-1557803175-2dfa0cc0756a?w=400&h=400&fit=crop"],
    "bike_gloves": ["https://picsum.photos/photo-1623998021450-85c29c661e90?w=400&h=400&fit=crop"],
    "tent": ["https://picsum.photos/photo-1478131143081-80f7f84ca84d?w=400&h=400&fit=crop"],
    "sleeping_bag": ["https://picsum.photos/photo-1520256862855-398228c0cce6?w=400&h=400&fit=crop"],
    "backpack": ["https://picsum.photos/photo-1553062407-98eeb64c6a62?w=400&h=400&fit=crop"],
}

PRODUCTS_DATA = {
    "smartphones": [
        {
            "name": "iPhone 15 Pro",
            "description": "iPhone 15 Pro с титановым корпусом, чипом A17 Pro, камерой 48 МП и поддержкой USB-C. Самый мощный и лёгкий Pro в истории.",
            "price": 129990, "quantity": 15,
            "images": IMG["iphone"],
            "attrs": {"Экран": '6.1" OLED 120Hz', "Процессор": "A17 Pro", "Память": "256 ГБ", "Камера": "48+12+12 МП", "Аккумулятор": "3274 мАч", "Вес": "187 г"},
        },
        {
            "name": "Samsung Galaxy S24",
            "description": "Флагман Samsung с Dynamic AMOLED 2X экраном, Exynos 2400, тройной камерой 50 МП и Galaxy AI.",
            "price": 109990, "quantity": 20,
            "images": IMG["samsung"],
            "attrs": {"Экран": '6.2" AMOLED 120Hz', "Процессор": "Exynos 2400", "Память": "256 ГБ", "Камера": "50+12+10 МП", "Аккумулятор": "4000 мАч"},
        },
        {
            "name": "Xiaomi 14 Pro",
            "description": "Xiaomi 14 Pro с Leica-оптикой, Snapdragon 8 Gen 3 и AMOLED-экраном 120 Гц. Идеален для фото.",
            "price": 69990, "quantity": 30,
            "images": IMG["xiaomi"],
            "attrs": {"Экран": '6.73" AMOLED', "Процессор": "Snapdragon 8 Gen 3", "Память": "512 ГБ", "Камера": "50+50+50 МП Leica"},
        },
        {
            "name": "Google Pixel 8",
            "description": "Google Pixel 8 с чипом Tensor G3, чистым Android 14 и лучшими AI-функциями для фото.",
            "price": 79990, "quantity": 10,
            "images": IMG["pixel"],
            "attrs": {"Экран": '6.2" OLED 120Hz', "Процессор": "Tensor G3", "Память": "128 ГБ", "Камера": "50+12 МП"},
        },
        {
            "name": "OnePlus 12",
            "description": "OnePlus 12 с Hasselblad-камерой, Snapdragon 8 Gen 3 и сверхбыстрой зарядкой 100 Вт.",
            "price": 89990, "quantity": 8,
            "images": IMG["oneplus"],
            "attrs": {"Экран": '6.82" AMOLED', "Процессор": "Snapdragon 8 Gen 3", "Память": "256 ГБ", "Камера": "50+48+64 МП"},
        },
    ],
    "laptops": [
        {
            "name": "MacBook Pro 16 M3",
            "description": "MacBook Pro 16 дюймов на чипе M3 Max. Liquid Retina XDR, 36 ГБ RAM. Создан для профессионалов.",
            "price": 249990, "quantity": 5,
            "images": IMG["macbook"],
            "attrs": {"Экран": '16.2" Liquid Retina XDR', "Процессор": "M3 Max", "RAM": "36 ГБ", "SSD": "1 ТБ", "Батарея": "до 22 ч"},
        },
        {
            "name": "Dell XPS 15",
            "description": "Dell XPS 15 — ультрабук с OLED-дисплеем, Intel Core i7-13700H и дискретной графикой Arc A370M.",
            "price": 189990, "quantity": 7,
            "images": IMG["dell"],
            "attrs": {"Экран": '15.6" OLED 3.5K', "Процессор": "i7-13700H", "RAM": "16 ГБ", "SSD": "512 ГБ", "Вес": "1.8 кг"},
        },
        {
            "name": "Lenovo ThinkPad X1",
            "description": "Бизнес-ноутбук ThinkPad X1 Carbon Gen 11: лёгкий, прочный, с классной клавиатурой и до 15 ч работы.",
            "price": 169990, "quantity": 12,
            "images": IMG["thinkpad"],
            "attrs": {"Экран": '14" IPS', "Процессор": "i7-1365U", "RAM": "16 ГБ", "SSD": "512 ГБ", "Вес": "1.12 кг"},
        },
        {
            "name": "ASUS ROG Zephyrus",
            "description": "Игровой ноутбук ASUS ROG Zephyrus G14 с Ryzen 9 и RTX 4060 для максимальной производительности.",
            "price": 219990, "quantity": 3,
            "images": IMG["asus"],
            "attrs": {"Экран": '14" QHD 165Hz', "Процессор": "Ryzen 9 7940HS", "RAM": "32 ГБ", "Видеокарта": "RTX 4060 8GB", "SSD": "1 ТБ"},
        },
    ],
    "headphones": [
        {
            "name": "AirPods Pro 2", "description": "AirPods Pro 2 с чипом H2, активным шумоподавлением и адаптивным звуком. До 6 ч работы.",
            "price": 24990, "quantity": 40, "images": IMG["airpods"],
            "attrs": {"Тип": "TWS-вкладыши", "Шумоподавление": "Активное", "Чип": "H2", "Батарея": "до 6 ч", "Защита": "IPX4"},
        },
        {
            "name": "Sony WH-1000XM5", "description": "Лучшие полноразмерные наушники Sony с непревзойдённым шумоподавлением и 30 ч автономной работы.",
            "price": 34990, "quantity": 25, "images": IMG["sony"],
            "attrs": {"Тип": "Полноразмерные", "Шумоподавление": "Активное", "Батарея": "до 30 ч", "Кодек": "LDAC", "Вес": "250 г"},
        },
        {
            "name": "Bose QC45", "description": "Bose QuietComfort 45 — легендарный комфорт и шумоподавление. 24 ч работы, мягкие амбушюры.",
            "price": 29990, "quantity": 18, "images": IMG["bose"],
            "attrs": {"Тип": "Полноразмерные", "Шумоподавление": "Активное", "Батарея": "до 24 ч", "USB-C": "Да", "Вес": "238 г"},
        },
        {
            "name": "JBL Tune 770", "description": "Бюджетные накладные наушники JBL с Pure Bass и 40 ч работы без подзарядки.",
            "price": 7990, "quantity": 60, "images": IMG["jbl"],
            "attrs": {"Тип": "Накладные", "Батарея": "до 40 ч", "Bluetooth": "5.3", "Быстрая зарядка": "5 мин = 2 ч"},
        },
    ],
    "tablets": [
        {
            "name": "iPad Air M2", "description": "iPad Air на чипе M2 с Liquid Retina 11-дюймовым дисплеем. Поддержка Apple Pencil Pro.",
            "price": 79990, "quantity": 14, "images": IMG["ipad"],
            "attrs": {"Экран": '11" Liquid Retina', "Процессор": "M2", "Память": "128 ГБ", "Камера": "12 МП", "Wi-Fi": "6E"},
        },
        {
            "name": "Samsung Tab S9", "description": "Samsung Galaxy Tab S9 с Dynamic AMOLED 120 Гц, Snapdragon 8 Gen 2 и S Pen в комплекте.",
            "price": 69990, "quantity": 10, "images": IMG["tab_s9"],
            "attrs": {"Экран": '11" AMOLED 120Hz', "Процессор": "Snapdragon 8 Gen 2", "Память": "128 ГБ", "S Pen": "В комплекте"},
        },
        {
            "name": "Xiaomi Pad 6", "description": "Доступный планшет Xiaomi Pad 6 с 11-дюймовым 144 Гц дисплеем и Snapdragon 870.",
            "price": 34990, "quantity": 22, "images": IMG["xpad"],
            "attrs": {"Экран": '11" IPS 144Hz', "Процессор": "Snapdragon 870", "Память": "128 ГБ", "Аккумулятор": "8840 мАч"},
        },
    ],
    "mens-clothing": [
        {
            "name": "Куртка кожаная", "description": "Классическая кожаная куртка из натуральной телячьей кожи. Подкладка из вискозы.",
            "price": 15990, "quantity": 20, "images": IMG["jacket"],
            "attrs": {"Материал": "Натуральная кожа", "Подкладка": "Вискоза", "Сезон": "Осень/весна", "Размеры": "S-XXL"},
        },
        {
            "name": "Джинсы классические", "description": "Прямые джинсы из японского денима, 13 oz. Классическая посадка, пять карманов.",
            "price": 6990, "quantity": 35, "images": IMG["jeans"],
            "attrs": {"Материал": "100% хлопок", "Плотность": "13 oz", "Посадка": "Прямая", "Цвет": "Индиго"},
        },
        {
            "name": "Футболка хлопок", "description": "Базовая футболка из 100% органического хлопка. Плотный трикотаж 180 г/м², не теряет форму.",
            "price": 1990, "quantity": 100, "images": IMG["tshirt"],
            "attrs": {"Материал": "Органический хлопок", "Плотность": "180 г/м²", "Цвета": "Белый, чёрный, серый"},
        },
        {
            "name": "Свитер шерстяной", "description": "Тёплый свитер из 100% мериносовой шерсти. Идеален для холодной погоды.",
            "price": 8990, "quantity": 15, "images": IMG["sweater"],
            "attrs": {"Материал": "Мериносовая шерсть", "Плотность": "Средняя", "Стирка": "Ручная"},
        },
    ],
    "womens-clothing": [
        {
            "name": "Платье вечернее", "description": "Элегантное вечернее платье из итальянского шёлка с кружевной отделкой. А-силуэт.",
            "price": 12990, "quantity": 12, "images": IMG["dress"],
            "attrs": {"Материал": "Шёлк + кружево", "Длина": "Миди", "Силуэт": "А-силуэт", "Размеры": "XS-L"},
        },
        {
            "name": "Блузка шёлковая", "description": "Шёлковая блузка свободного кроя. Отложной воротник, длинные рукава на манжетах.",
            "price": 5990, "quantity": 25, "images": IMG["blouse"],
            "attrs": {"Материал": "100% шёлк", "Крой": "Свободный", "Цвета": "Белый, бежевый"},
        },
        {
            "name": "Юбка-карандаш", "description": "Классическая юбка-карандаш из костюмной ткани. Застёжка-молния сзади, шлица.",
            "price": 4990, "quantity": 30, "images": IMG["skirt"],
            "attrs": {"Материал": "Костюмная ткань", "Длина": "Миди", "Цвет": "Чёрный"},
        },
    ],
    "shoes": [
        {
            "name": "Кроссовки Nike Air", "description": "Культовые кроссовки Nike Air Max 90 с видимой воздушной подушкой и комфортной колодкой.",
            "price": 12990, "quantity": 40, "images": IMG["nike"],
            "attrs": {"Бренд": "Nike", "Модель": "Air Max 90", "Материал": "Кожа+текстиль", "Размеры": "39-46"},
        },
        {
            "name": "Ботинки Timberland", "description": "Классические ботинки Timberland 6 inch. Водонепроницаемый нубук, прочная подошва.",
            "price": 18990, "quantity": 15, "images": IMG["timberland"],
            "attrs": {"Бренд": "Timberland", "Материал": "Нубук", "Подошва": "Резина", "Водозащита": "Да"},
        },
        {
            "name": "Туфли классические", "description": "Мужские классические туфли из натуральной кожи. Оксфорды, подошва из кожи.",
            "price": 9990, "quantity": 20, "images": IMG["classic_shoes"],
            "attrs": {"Тип": "Оксфорды", "Материал": "Натуральная кожа", "Цвет": "Чёрный", "Размеры": "40-45"},
        },
    ],
    "furniture": [
        {
            "name": "Диван угловой", "description": "Угловой диван с обивкой из велюра, раскладной механизм «дельфин», вместительный ящик для белья.",
            "price": 89990, "quantity": 3, "images": IMG["sofa"],
            "attrs": {"Материал": "Велюр", "Механизм": "Дельфин", "Размер": "260×180 см", "Спальное место": "160×200 см"},
        },
        {
            "name": "Стол обеденный", "description": "Обеденный стол из массива дуба. Раздвижной механизм, вмещает до 8 человек.",
            "price": 24990, "quantity": 8, "images": IMG["table"],
            "attrs": {"Материал": "Массив дуба", "Размер": "120-180×80 см", "Высота": "75 см"},
        },
        {
            "name": "Стул офисный", "description": "Эргономичное офисное кресло с поясничной поддержкой, газлифтом и сетчатой спинкой.",
            "price": 15990, "quantity": 20, "images": IMG["chair"],
            "attrs": {"Материал": "Сетка + пластик", "Газлифт": "Да", "Макс. нагрузка": "120 кг"},
        },
        {
            "name": "Кровать двуспальная", "description": "Двуспальная кровать с мягким изголовьем из экокожи. Подъёмный механизм, ящик для белья.",
            "price": 54990, "quantity": 4, "images": IMG["bed"],
            "attrs": {"Материал": "Экокожа + ЛДСП", "Размер": "160×200 см", "Подъёмный механизм": "Да"},
        },
    ],
    "lighting": [
        {
            "name": "Люстра хрустальная", "description": "Роскошная хрустальная люстра на 8 ламп. Подвесная, регулируемая высота.",
            "price": 34990, "quantity": 6, "images": IMG["chandelier"],
            "attrs": {"Материал": "Хрусталь + металл", "Лампы": "8×E14", "Высота": "60-100 см", "Стиль": "Классика"},
        },
        {
            "name": "Торшер напольный", "description": "Современный торшер с LED-лампой, тёплый свет 3000K. Металлический корпус.",
            "price": 7990, "quantity": 15, "images": IMG["floor_lamp"],
            "attrs": {"Тип": "LED", "Мощность": "12 Вт", "Цвет. темп.": "3000K", "Высота": "160 см"},
        },
        {
            "name": "Светильник LED", "description": "Потолочный LED-светильник с регулировкой яркости и пультом ДУ. 36 Вт, 4000K.",
            "price": 2990, "quantity": 50, "images": IMG["led_light"],
            "attrs": {"Мощность": "36 Вт", "Яркость": "3600 лм", "Диммирование": "Да", "Пульт ДУ": "Да"},
        },
    ],
    "decor": [
        {
            "name": "Картина маслом", "description": "Авторская картина маслом на холсте. Пейзаж, размер 60×80 см. Ручная работа.",
            "price": 19990, "quantity": 5, "images": IMG["painting"],
            "attrs": {"Техника": "Масло", "Основа": "Холст", "Размер": "60×80 см", "Автор": "А. Иванов"},
        },
        {
            "name": "Ваза керамическая", "description": "Дизайнерская керамическая ваза ручной работы. Высота 35 см, матовое покрытие.",
            "price": 4990, "quantity": 18, "images": IMG["vase"],
            "attrs": {"Материал": "Керамика", "Высота": "35 см", "Покрытие": "Матовое", "Ручная работа": "Да"},
        },
        {
            "name": "Зеркало настенное", "description": "Настенное зеркало в металлической раме под золото. Диаметр 70 см.",
            "price": 8990, "quantity": 10, "images": IMG["mirror"],
            "attrs": {"Диаметр": "70 см", "Рама": "Металл (золото)", "Крепление": "Настенное"},
        },
    ],
    "fitness": [
        {
            "name": "Гантели 10 кг", "description": "Наборные гантели с обрезиненными дисками. Вес одной гантели 10 кг в сборе.",
            "price": 4990, "quantity": 30, "images": IMG["dumbbell"],
            "attrs": {"Вес": "10 кг", "Тип": "Наборные", "Материал дисков": "Резина+металл", "Гриф": "Хромированный"},
        },
        {
            "name": "Коврик для йоги", "description": "Нескользящий коврик для йоги толщиной 6 мм из термопластичной резины TPE.",
            "price": 2990, "quantity": 45, "images": IMG["yoga_mat"],
            "attrs": {"Толщина": "6 мм", "Материал": "TPE", "Размер": "183×61 см", "Чехол": "В комплекте"},
        },
        {
            "name": "Скакалка", "description": "Скоростная скакалка с подшипниками и регулируемой длиной. Трос стальной в ПВХ.",
            "price": 990, "quantity": 80, "images": IMG["rope"],
            "attrs": {"Трос": "Сталь+ПВХ", "Ручки": "Нескользящие", "Длина": "Регулируемая", "Подшипники": "Да"},
        },
        {
            "name": "Фитбол", "description": "Гимнастический мяч-фитбол, 65 см. В комплекте насос. Выдерживает до 150 кг.",
            "price": 1990, "quantity": 25, "images": IMG["fitball"],
            "attrs": {"Диаметр": "65 см", "Макс. нагрузка": "150 кг", "Насос": "В комплекте"},
        },
    ],
    "cycling": [
        {
            "name": "Велосипед горный", "description": "Горный велосипед Stinger 29 дюймов, алюминиевая рама, 21 скорость, дисковые тормоза.",
            "price": 59990, "quantity": 5, "images": IMG["bike"],
            "attrs": {"Колёса": '29"', "Рама": "Алюминий", "Скорости": "21", "Тормоза": "Дисковые"},
        },
        {
            "name": "Шлем велосипедный", "description": "Защитный шлем с MIPS, 18 вентиляционных отверстий, регулировка посадки.",
            "price": 4990, "quantity": 20, "images": IMG["helmet"],
            "attrs": {"Технология": "MIPS", "Вентиляция": "18 отв.", "Размер": "54-61 см", "Вес": "280 г"},
        },
        {
            "name": "Вело-перчатки", "description": "Гелевые велоперчатки с дышащей сеткой. Защита от мозолей, анатомический крой.",
            "price": 1490, "quantity": 35, "images": IMG["bike_gloves"],
            "attrs": {"Материал": "Лайкра+гель", "Размеры": "S-XL", "Застёжка": "Липучка"},
        },
    ],
    "tourism": [
        {
            "name": "Палатка 3-местная", "description": "Трёхместная туристическая палатка с тамбуром. Водостойкость 3000 мм, вес 3.8 кг.",
            "price": 15990, "quantity": 8, "images": IMG["tent"],
            "attrs": {"Вместимость": "3 чел.", "Вес": "3.8 кг", "Водостойкость": "3000 мм", "Тамбур": "Да"},
        },
        {
            "name": "Спальник", "description": "Спальный мешок-одеяло, температура комфорта от +5°C. Утеплитель Hollow Fiber.",
            "price": 6990, "quantity": 14, "images": IMG["sleeping_bag"],
            "attrs": {"Наполнитель": "Hollow Fiber", "Темп. комфорта": "+5°C", "Вес": "1.5 кг", "Размер": "220×85 см"},
        },
        {
            "name": "Рюкзак 60л", "description": "Туристический рюкзак 60 литров с анатомической спинкой, дождевиком и множеством карманов.",
            "price": 8990, "quantity": 12, "images": IMG["backpack"],
            "attrs": {"Объём": "60 л", "Вес": "2.1 кг", "Дождевик": "В комплекте", "Спинка": "Анатомическая"},
        },
    ],
}

async def seed():
    async with AsyncSessionLocal() as db:
        # Удаляем старые данные
        await db.execute(delete(CatalogProduct))
        await db.execute(delete(Category))
        await db.commit()

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
        total = 0
        for slug, products in PRODUCTS_DATA.items():
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
                    image_urls=p["images"],
                    attributes=p["attrs"],
                )
                db.add(product)
                total += 1

        await db.commit()
        print(f"\n✔ Создано категорий: {len(created)}, товаров: {total}")


if __name__ == "__main__":
    asyncio.run(seed())