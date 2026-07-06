# Marketplace

Маркетплейс — веб-приложение для онлайн-торговли с каталогом товаров, поиском и системой аутентификации.

## Технологический стек

| Слой | Технологии |
|------|-------------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL 16 |
| **Frontend** | React 18, TypeScript, Vite, React Router, Axios |
| **Аутентификация** | JWT (access + refresh), bcrypt, VK OAuth2 |
| **Инфраструктура** | Docker Compose (backend + frontend + PostgreSQL) |

## Запуск проекта

```bash
# 1. Клонировать репозиторий
git clone https://github.com/aleksandrakalininaa/Marketplace.git
cd Marketplace

# 2. Создать .env файл с переменными окружения
cp .env.example .env
# Отредактировать .env — указать VK_APP_ID, VK_SECRET

# 3. Запустить все сервисы
docker compose up --build -d

# 4. Наполнить базу тестовыми данными
docker compose exec backend python scripts/seed_catalog.py
```

После запуска:
- **Фронтенд**: http://localhost:3000
- **Бэкенд API**: http://localhost:8000
- **Swagger-документация**: http://localhost:8000/docs

## Реализованный функционал

### 1. Аутентификация (User Story 1.x)

**Модели:**
- `User` — пользователь (UUID, email опциональный, password_hash, name, is_seller)
- `VkAccount` — привязка VK ID к аккаунту
- `RefreshToken` — JWT refresh-токены с SHA-256 хешированием
- `PasswordResetToken` — токены сброса пароля

**Эндпоинты (`/auth`):**

| Метод | Путь | Описание |
|-------|------|----------|
| POST | /register | Регистрация по email и паролю |
| POST | /login | Вход → access_token (15 мин) + refresh_token (7 дней) |
| POST | /refresh | Ротация refresh-токенов |
| POST | /vk | Вход через VK ID (OAuth2), авто-линковка по email |
| POST | /forgot-password | Отправка ссылки сброса пароля |
| POST | /reset-password | Сброс пароля по токену |
| POST | /link-vk | Привязка VK к текущему аккаунту |
| GET | /me | Данные пользователя + флаг vk_linked |

**Особенности безопасности:**
- Пароли хешируются bcrypt
- refresh_token хранится как SHA-256 хеш, клиенту отдаётся сам токен
- При обновлении токенов старый инвалидируется, выпускается новый (ротация)
- Все эндпоинты (кроме register, login, forgot/reset, vk) требуют JWT в Authorization: Bearer

**Фронтенд:**
- Страница входа/регистрации на едином URL (`/`)
- Кнопка «Войти через VK» с редиректом на OAuth и callback-обработчиком
- Access-токен в sessionStorage, refresh в localStorage
- Axios-интерсептор: автоматическое обновление токена при 401
- ProtectedRoute для защищённых страниц

---

### 2. Каталог товаров (User Story 2.1)

**Модели:**
- `Category` — древовидная структура (parent_id FK на себя)
- `CatalogProduct` — товар (UUID, цена Numeric, image_urls JSONB, attributes JSONB)

**Эндпоинты (`/api/v1`):**

| Метод | Путь | Описание |
|-------|------|----------|
| GET | /categories | Дерево категорий (рекурсивное) |
| GET | /products | Список товаров с фильтрацией и пагинацией |

**Фильтры:** category_id (с потомками), min/max цена, в наличии, сортировка (5 вариантов)

**Фронтенд:**
- Сайдбар с деревом категорий (подкатегории свёрнуты по умолчанию, раскрываются по клику)
- Сетка карточек товаров: 4 колонки → адаптивно
- Фильтры по цене, наличию, сортировке
- Пагинация
- Все параметры в URL query string (можно делиться ссылкой)
- Состояния: скелетон загрузки, ошибка, пустой список
- Тёмная премиум-тема

---

### 3. Карточка товара (User Story 2.2)

**Эндпоинт:** `GET /api/v1/products/{id}`

**Фронтенд (`/products/:id`):**
- Галерея изображений (основное фото + миниатюры)
- Полная информация: название, цена, статус наличия
- Таблица характеристик (из attributes)
- Описание товара
- Кнопка «Добавить в корзину»
- Скелетон загрузки, обработка ошибок 404/500
- Кнопка «← Назад» с возвратом на предыдущую страницу с сохранением фильтров

---

### 4. Поиск товаров (User Story 2.3)

**Эндпоинт:** `GET /api/v1/products` — параметр `search` (ILIKE по name и description)

**Фронтенд:**
- Строка поиска в хедере с debounce 300ms
- Поиск работает прямо в каталоге — категории слева остаются видимыми
- При вводе текста мгновенно обновляется URL и список товаров
- Можно комбинировать поиск + выбор категории
- Фильтры и пагинация работают вместе с поиском
- Состояния: «Введите запрос», загрузка, «Ничего не найдено»

---

## Структура проекта

```
Marketplace/
├── app/                    # Бэкенд FastAPI
│   ├── main.py             # Точка входа, CORS, lifespan
│   ├── config.py           # Настройки (pydantic-settings)
│   ├── database.py         # Async SQLAlchemy engine + сессии
│   ├── models/             # SQLAlchemy модели
│   │   ├── user.py         # User
│   │   ├── vk_account.py   # VkAccount, RefreshToken, PasswordResetToken
│   │   ├── catalog.py      # Category, CatalogProduct
│   │   ├── product.py      # Product (наследие)
│   │   ├── order.py        # Order, OrderItem
│   │   └── review.py       # Review
│   ├── schemas/            # Pydantic-схемы
│   │   ├── user.py
│   │   ├── catalog.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── review.py
│   ├── services/           # Бизнес-логика
│   │   ├── auth.py         # JWT, bcrypt, VK OAuth2
│   │   └── catalog.py      # Поиск, фильтры, дерево категорий
│   └── routers/            # FastAPI роутеры
│       ├── auth.py
│       ├── catalog.py
│       ├── products.py
│       ├── orders.py
│       └── reviews.py
├── frontend/               # React SPA
│   ├── src/
│   │   ├── api/            # Axios-клиент и модули API
│   │   ├── context/        # AuthContext
│   │   ├── components/     # Переиспользуемые компоненты
│   │   │   ├── SearchBar.tsx
│   │   │   ├── CategoryTree.tsx
│   │   │   ├── ProductCard.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   └── pages/          # Страницы
│   │       ├── HomePage.tsx            # Вход / Каталог
│   │       ├── CatalogPage.tsx         # Каталог с поиском
│   │       ├── ProductPage.tsx         # Карточка товара
│   │       ├── VkCallbackPage.tsx      # VK OAuth callback
│   │       └── ResetPasswordPage.tsx   # Сброс пароля
│   └── Dockerfile
├── scripts/
│   └── seed_catalog.py     # Наполнение БД (17 категорий, 46 товаров)
├── docker-compose.yml      # PostgreSQL + Backend + Frontend
├── Dockerfile              # Бэкенд Docker
└── requirements.txt        # Python-зависимости
```

## Переменные окружения

Создать `.env` файл в корне проекта:

```env
VK_APP_ID=           # ID приложения VK
VK_SECRET=           # Защищённый ключ VK
SECRET_KEY=           # JWT секрет
DATABASE_URL=         # PostgreSQL URL
FRONTEND_URL=         # http://localhost:3000
VK_REDIRECT_URI=      # http://localhost:3000/auth/vk-callback