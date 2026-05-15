# 🚗 Автосервис: управление заказами

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-24.0-blue.svg)](https://www.docker.com/)

## 📝 Описание проекта

REST API для управления заказами в автосервисе. Позволяет создавать, просматривать, обновлять и удалять заказы на ремонт автомобилей.

**Предметная область:** Вариант 28 — Система управления автосервисом

**Основные сущности:**
- Заказ (Order): госномер авто, ФИО владельца, описание проблемы, статус, итоговая цена, дата создания
- Мастер (Master): ФИО, специализация, телефон, дата найма

## 🛠 Технологический стек

| Технология | Назначение |
|------------|------------|
| FastAPI | Веб-фреймворк |
| PostgreSQL | База данных |
| SQLAlchemy | ORM |
| Alembic | Миграции |
| Pydantic | Валидация данных |
| Docker | Контейнеризация |
| pytest | Тестирование |

## 📋 Требования

- Python 3.11+
- Docker (для запуска через контейнер)
- PostgreSQL 15 (для локального запуска)

## 🚀 Установка и запуск

### Способ 1: Локальный запуск (без Docker)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/holhalovaa/LR_12
cd autoservice-api

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Создать файл .env и настроить подключение к БД
cp .env.example .env
# Отредактируйте .env: DATABASE_URL=postgresql://user:pass@localhost:5432/autoservice_db

# 5. Применить миграции
alembic upgrade head

# 6. Запустить приложение
uvicorn main:app --reload --port 8000
```

### Способ 2: Запуск через Docker (рекомендуемый)

```bash
# 1. Скопировать переменные окружения
cp .env.example .env

# 2. Запустить контейнеры
docker-compose up --build
```

Приложение будет доступно на `http://localhost:8000`, PostgreSQL на порту `5432`

### Способ 3: Запуск тестов

```bash
# Установить тестовые зависимости
pip install pytest pytest-cov httpx

# Запустить тесты
pytest test_main.py -v --cov=main --cov-report=term-missing
```

**Результат тестов:** 18 passed, покрытие 94%

```
============================= test session starts =============================
collected 18 items

test_main.py::test_get_all_orders_empty PASSED
test_main.py::test_get_all_orders_returns_list PASSED
test_main.py::test_get_order_by_id_success PASSED
test_main.py::test_get_order_by_id_not_found PASSED
test_main.py::test_get_order_by_id_invalid_type PASSED
test_main.py::test_create_order_success PASSED
test_main.py::test_create_order_missing_required_fields PASSED
test_main.py::test_create_order_invalid_status PASSED
test_main.py::test_create_order_negative_price PASSED
test_main.py::test_update_order_full_success PASSED
test_main.py::test_update_order_not_found PASSED
test_main.py::test_partial_update_order_status_only PASSED
test_main.py::test_partial_update_order_price_only PASSED
test_main.py::test_partial_update_order_invalid_status PASSED
test_main.py::test_delete_order_success PASSED
test_main.py::test_delete_order_not_found PASSED
test_main.py::test_create_order_with_long_description PASSED
test_main.py::test_update_order_negative_price PASSED

============================= 18 passed in 1.25s ==============================
```

## 📡 API Эндпоинты

**Базовая URL:** `http://localhost:8000`

### GET /orders — получить все заказы

**Ответ:**
```json
[
  {
    "id": 1,
    "car_number": "А123ВС777",
    "owner_name": "Иван Петров",
    "description": "Не заводится двигатель",
    "status": "принят",
    "total_price": 0,
    "created_at": "2026-05-15T16:00:00"
  }
]
```

### POST /orders — создать заказ

**Запрос:**
```json
{
  "car_number": "А123ВС777",
  "owner_name": "Иван Петров",
  "description": "Не заводится двигатель",
  "status": "принят",
  "total_price": 0
}
```

**Ответ:** `201 Created` + данные созданного заказа

### GET /orders/{id} — получить заказ по ID

**Ответ:** `200 OK` + данные заказа

**Ошибка:** `404 Not Found`

### PUT /orders/{id} — полное обновление

**Запрос:** все поля обязательны

**Ответ:** `200 OK`

### PATCH /orders/{id} — частичное обновление

**Запрос:**
```json
{
  "status": "готов"
}
```

**Ответ:** `200 OK`

### DELETE /orders/{id} — удалить заказ

**Ответ:** `204 No Content`

### GET /health — проверка работоспособности

**Ответ:**
```json
{
  "status": "ok",
  "timestamp": "2026-05-15T16:58:37.209443"
}
```

## 🔐 Переменные окружения (.env)

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `DATABASE_URL` | URL подключения к PostgreSQL | `postgresql://postgres:postgres123@db:5432/autoservice_db` |
| `POSTGRES_USER` | Пользователь БД | `postgres` |
| `POSTGRES_PASSWORD` | Пароль БД | `postgres123` |
| `POSTGRES_DB` | Название базы данных | `autoservice_db` |
| `APP_ENV` | Окружение (development/production) | `development` |
| `APP_PORT` | Порт приложения | `8000` |

## 📁 Структура проекта

```
autoservice-api/
├── main.py                      # FastAPI приложение (CRUD, CORS, XSS защита)
├── models.py                    # SQLAlchemy модели (Order, Master)
├── database.py                  # Подключение к БД (SQLAlchemy engine, Session)
├── test_main.py                 # Pytest тесты (18 тестов, покрытие 94%)
├── bad_code.py                  # Плохой код для рефакторинга (задание 3)
├── good_code.py                 # Отрефакторенный код (задание 3)
├── validate_plate.py            # Регулярное выражение для госномера (задание 10)
├── sql_report_top_masters.sql   # SQL-запрос топ-3 мастеров (задание 9)
├── requirements.txt             # Зависимости проекта
├── Dockerfile                   # Docker образ для FastAPI
├── docker-compose.yml           # Docker Compose (app + PostgreSQL)
├── alembic.ini                  # Конфигурация Alembic
├── alembic/                     # Миграции Alembic
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 52ee699c07a3_create_orders_table.py
│       └── 2a3b4c5d6e7f_add_masters_table.py
├── migrations/                  # Raw SQL миграции (опционально)
│   └── add_masters_table.sql
├── .env.example                 # Пример переменных окружения
├── .gitignore                   # Игнорируемые файлы
├── PROMPT_LOG.md                # Лог всех промптов (44 промпта)
└── README.md                    # Документация проекта
```

## 👤 Автор

**Вариант 28:** Система управления автосервисом

**Выполнила:** Холхалова Алина

**Группа:** 220032-11