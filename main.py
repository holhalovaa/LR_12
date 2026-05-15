"""
Автосервис: управление заказами
FastAPI CRUD приложение с PostgreSQL и Alembic
Исправленная версия с устранением уязвимостей:
- Добавлен CORS middleware
- Использование OrderResponse для защиты от утечки данных
- Экранирование HTML в description (защита от XSS)
- Объединена логика обновления (устранено дублирование кода)
"""

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
import html

from database import get_db
from models import Order as OrderModel, OrderStatus

app = FastAPI(title="Автосервис API", description="Управление заказами в автосервисе")

# ========== CORS настройка (защита от Cross-Origin запросов) ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # React фронтенд
        "http://localhost:8080",   # Другой фронтенд
        "http://localhost:8000",   # Сам API
    ],
    allow_credentials=True,
    allow_methods=["*"],           # Разрешены все методы
    allow_headers=["*"],           # Разрешены все заголовки
)

# ========== Pydantic модели ==========

class OrderCreate(BaseModel):
    """Модель для создания заказа"""
    car_number: str = Field(..., min_length=1, max_length=15, description="Госномер авто")
    owner_name: str = Field(..., min_length=2, max_length=100, description="ФИО владельца")
    description: str = Field(..., min_length=1, description="Описание проблемы")
    status: str = Field(default="принят", description="Статус заказа")
    total_price: float = Field(default=0.0, ge=0, description="Итоговая цена")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = ["принят", "в работе", "готов", "выдан"]
        if v not in allowed:
            raise ValueError(f"Статус должен быть одним из: {allowed}")
        return v

    @field_validator("car_number")
    @classmethod
    def validate_car_number(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError("Госномер слишком короткий")
        return v.upper()


class OrderUpdate(BaseModel):
    """Модель для обновления заказа (поля опциональны)"""
    car_number: Optional[str] = Field(None, min_length=1, max_length=15)
    owner_name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = None
    total_price: Optional[float] = Field(None, ge=0)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["принят", "в работе", "готов", "выдан"]
            if v not in allowed:
                raise ValueError(f"Статус должен быть одним из: {allowed}")
        return v


class OrderResponse(BaseModel):
    """Модель для ответа (только безопасные поля)"""
    id: int
    car_number: str
    owner_name: str
    description: str
    status: str
    total_price: float
    created_at: datetime

    class Config:
        from_attributes = True  # Для Pydantic v2


# ========== Вспомогательная функция для обновления (устранение дублирования) ==========

def _update_order_fields(db_order: OrderModel, order_update: OrderUpdate, db: Session) -> OrderModel:
    """
    Общая логика обновления полей заказа для PUT и PATCH эндпоинтов.
    Обновляет только те поля, которые переданы (не None).
    """
    if order_update.car_number is not None:
        db_order.car_number = order_update.car_number
    if order_update.owner_name is not None:
        db_order.owner_name = order_update.owner_name
    if order_update.description is not None:
        db_order.description = html.escape(order_update.description)  # XSS защита
    if order_update.status is not None:
        try:
            db_order.status = OrderStatus(order_update.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Недопустимый статус: {order_update.status}"
            )
    if order_update.total_price is not None:
        db_order.total_price = order_update.total_price
    
    db.commit()
    db.refresh(db_order)
    return db_order


# ========== Эндпоинты ==========

@app.get("/orders", response_model=List[OrderResponse], tags=["Orders"])
async def get_all_orders(db: Session = Depends(get_db)):
    """Получить список всех заказов (только безопасные поля)"""
    orders = db.query(OrderModel).all()
    return orders


@app.get("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """Получить заказ по ID (только безопасные поля)"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ с id={order_id} не найден"
        )
    return order


@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Orders"])
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Создать новый заказ (с экранированием HTML)"""
    # Конвертируем строку статуса в enum
    try:
        status_enum = OrderStatus(order.status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Недопустимый статус: {order.status}"
        )
    
    db_order = OrderModel(
        car_number=order.car_number,
        owner_name=order.owner_name,
        description=html.escape(order.description),  # XSS защита
        status=status_enum,
        total_price=order.total_price,
        created_at=datetime.now()
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@app.put("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
async def update_order(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    """Полностью обновить заказ (с экранированием HTML)"""
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ с id={order_id} не найден"
        )
    return _update_order_fields(db_order, order_update, db)


@app.patch("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
async def partial_update_order(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    """Частично обновить заказ (только переданные поля)"""
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ с id={order_id} не найден"
        )
    return _update_order_fields(db_order, order_update, db)


@app.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Orders"])
async def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Удалить заказ по ID"""
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ с id={order_id} не найден"
        )
    
    db.delete(db_order)
    db.commit()
    return None


# ========== Дополнительные эндпоинты для безопасности ==========

@app.get("/health", tags=["Health"])
async def health_check():
    """Проверка работоспособности сервера"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}