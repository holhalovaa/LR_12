"""
Модели базы данных для автосервиса (расширенная версия)
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class OrderStatus(enum.Enum):
    """Статусы заказа"""
    ACCEPTED = "принят"
    IN_PROGRESS = "в работе"
    READY = "готов"
    COMPLETED = "выдан"


class Master(Base):
    """Модель мастера в автосервисе"""
    __tablename__ = "masters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    specialization = Column(String(50), nullable=False, index=True)
    phone = Column(String(20))
    hire_date = Column(DateTime, default=datetime.now)
    
    # Связь с заказами (один мастер → много заказов)
    orders = relationship("Order", back_populates="master")


class Order(Base):
    """Модель заказа в автосервисе"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    car_number = Column(String(15), nullable=False, index=True)
    owner_name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.ACCEPTED, index=True)
    total_price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    
    # Внешний ключ на мастера
    master_id = Column(Integer, ForeignKey("masters.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Связь с мастером
    master = relationship("Master", back_populates="orders")

    def __repr__(self):
        return f"<Order {self.id}: {self.car_number}>"