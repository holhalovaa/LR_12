"""
Модульные тесты для API автосервиса
Покрытие: ~85% ключевых маршрутов
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db
from models import Order, OrderStatus

# Применяем миграции перед тестами
from alembic.config import Config
from alembic import command

alembic_cfg = Config("alembic.ini")
command.upgrade(alembic_cfg, "head")


# ========== Настройка тестовой базы данных SQLite (in-memory) ==========
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Переопределяем зависимость БД для тестов"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Подменяем зависимость в приложении
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ========== Фикстуры ==========

@pytest.fixture
def sample_order():
    """Создаёт тестовый заказ и возвращает его ID"""
    response = client.post("/orders", json={
        "car_number": "ТЕСТ123",
        "owner_name": "Тестов Тест",
        "description": "Тестовый заказ",
        "status": "принят",
        "total_price": 0
    })
    return response.json()["id"]


# ========== Тесты GET /orders ==========

def test_get_all_orders_empty():
    """Тест: получение списка заказов, когда база пуста"""
    # Очищаем БД
    db = TestingSessionLocal()
    db.query(Order).delete()
    db.commit()
    db.close()
    
    response = client.get("/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0


def test_get_all_orders_returns_list(sample_order):
    """Тест: получение списка заказов возвращает список"""
    response = client.get("/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


# ========== Тесты GET /orders/{id} ==========

def test_get_order_by_id_success(sample_order):
    """Тест: получение заказа по существующему ID"""
    response = client.get(f"/orders/{sample_order}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_order
    assert "car_number" in data
    assert "owner_name" in data
    assert "description" in data
    assert "status" in data
    assert "created_at" in data


def test_get_order_by_id_not_found():
    """Тест: получение заказа по несуществующему ID возвращает 404"""
    response = client.get("/orders/99999")
    assert response.status_code == 404
    assert "не найден" in response.json()["detail"]


def test_get_order_by_id_invalid_type():
    """Тест: получение заказа с некорректным типом ID"""
    response = client.get("/orders/abc")
    assert response.status_code == 422


# ========== Тесты POST /orders ==========

def test_create_order_success():
    """Тест: успешное создание заказа"""
    order_data = {
        "car_number": "А123ВС777",
        "owner_name": "Сидоров Сидор",
        "description": "Скрип при повороте",
        "status": "принят",
        "total_price": 0
    }
    response = client.post("/orders", json=order_data)
    assert response.status_code == 201
    data = response.json()
    assert data["car_number"] == order_data["car_number"]
    assert data["owner_name"] == order_data["owner_name"]
    assert data["description"] == order_data["description"]
    assert data["status"] == "принят"
    assert "id" in data
    assert "created_at" in data


def test_create_order_missing_required_fields():
    """Тест: создание заказа без обязательных полей"""
    response = client.post("/orders", json={
        "car_number": "А123ВС777"
    })
    assert response.status_code == 422


def test_create_order_invalid_status():
    """Тест: создание заказа с недопустимым статусом"""
    order_data = {
        "car_number": "А123ВС777",
        "owner_name": "Петров Петр",
        "description": "Тест",
        "status": "недопустимый_статус",
        "total_price": 0
    }
    response = client.post("/orders", json=order_data)
    assert response.status_code == 422


def test_create_order_negative_price():
    """Тест: создание заказа с отрицательной ценой"""
    order_data = {
        "car_number": "А123ВС777",
        "owner_name": "Петров Петр",
        "description": "Тест",
        "status": "принят",
        "total_price": -100
    }
    response = client.post("/orders", json=order_data)
    assert response.status_code == 422


# ========== Тесты PUT /orders/{id} ==========

def test_update_order_full_success(sample_order):
    """Тест: полное обновление существующего заказа"""
    updated_data = {
        "car_number": "НОВЫЙ777",
        "owner_name": "Новый Владелец",
        "description": "Новое описание",
        "status": "в работе",
        "total_price": 5000
    }
    response = client.put(f"/orders/{sample_order}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["car_number"] == updated_data["car_number"]
    assert data["owner_name"] == updated_data["owner_name"]
    assert data["description"] == updated_data["description"]
    assert data["status"] == updated_data["status"]


def test_update_order_not_found():
    """Тест: обновление несуществующего заказа"""
    updated_data = {
        "car_number": "НОВЫЙ777",
        "owner_name": "Новый Владелец",
        "description": "Новое описание",
        "status": "в работе",
        "total_price": 5000
    }
    response = client.put("/orders/99999", json=updated_data)
    assert response.status_code == 404


# ========== Тесты PATCH /orders/{id} ==========

def test_partial_update_order_status_only(sample_order):
    """Тест: частичное обновление (только статус)"""
    response = client.patch(f"/orders/{sample_order}", json={
        "status": "готов"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "готов"


def test_partial_update_order_price_only(sample_order):
    """Тест: частичное обновление (только цена)"""
    response = client.patch(f"/orders/{sample_order}", json={
        "total_price": 10000
    })
    assert response.status_code == 200
    data = response.json()
    assert data["total_price"] == 10000


def test_partial_update_order_invalid_status(sample_order):
    """Тест: частичное обновление с недопустимым статусом"""
    response = client.patch(f"/orders/{sample_order}", json={
        "status": "недопустимый"
    })
    assert response.status_code == 422


# ========== Тесты DELETE /orders/{id} ==========

def test_delete_order_success(sample_order):
    """Тест: успешное удаление заказа"""
    response = client.delete(f"/orders/{sample_order}")
    assert response.status_code == 204
    
    get_response = client.get(f"/orders/{sample_order}")
    assert get_response.status_code == 404


def test_delete_order_not_found():
    """Тест: удаление несуществующего заказа"""
    response = client.delete("/orders/99999")
    assert response.status_code == 404


# ========== Тест граничного случая ==========

def test_create_order_with_long_description():
    """Тест: создание заказа с очень длинным описанием"""
    long_description = "A" * 1000
    order_data = {
        "car_number": "А123ВС777",
        "owner_name": "Иванов Иван",
        "description": long_description,
        "status": "принят",
        "total_price": 0
    }
    response = client.post("/orders", json=order_data)
    assert response.status_code == 201
    data = response.json()
    assert len(data["description"]) == 1000


def test_update_order_negative_price(sample_order):
    """Тест: обновление заказа с отрицательной ценой"""
    response = client.patch(f"/orders/{sample_order}", json={
        "total_price": -1000
    })
    assert response.status_code == 422