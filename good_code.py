"""
ХОРОШИЙ код для автосервиса (ПОСЛЕ рефакторинга)
Задача: расчёт стоимости ремонта
"""

from enum import Enum
from typing import Union


# ========== Константы ==========

class Complexity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class HourlyRate:
    LOW = 1200
    MEDIUM = 1800
    HIGH = 2500
    DEFAULT = 1500


class DiscountLimits:
    MAX_PERCENT = 30
    LOYALTY_DISCOUNT = 0.95
    HIGH_COST_THRESHOLD = 50000
    HIGH_COST_DISCOUNT = 0.9


class Constants:
    URGENT_MULTIPLIER = 1.5
    EXTRA_FEE = 500
    EXTRA_FEE_ITERATIONS = 3


# ========== Основная функция ==========

def calculate_repair_cost(
    hours: Union[int, float],
    parts_cost: Union[int, float],
    complexity: int,
    is_urgent: bool,
    discount_percent: Union[int, float],
    is_loyal_customer: bool
) -> float:
    """
    Рассчитывает итоговую стоимость ремонта в автосервисе.
    
    Args:
        hours: Количество часов работы (>= 0)
        parts_cost: Стоимость запчастей (>= 0)
        complexity: Сложность (1-3)
        is_urgent: Срочный ремонт
        discount_percent: Скидка в процентах (0-100)
        is_loyal_customer: Постоянный клиент
    
    Returns:
        Итоговая стоимость ремонта
    
    Raises:
        ValueError: Если входные данные некорректны
    """
    # Валидация
    if hours < 0:
        raise ValueError(f"Часы не могут быть отрицательными: {hours}")
    if parts_cost < 0:
        raise ValueError(f"Стоимость запчастей не может быть отрицательной: {parts_cost}")
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError(f"Скидка должна быть от 0 до 100: {discount_percent}")
    
    # Расчёт
    hourly_rate = _get_hourly_rate(complexity)
    labor_cost = hours * hourly_rate
    if is_urgent:
        labor_cost *= Constants.URGENT_MULTIPLIER
    
    total = labor_cost + parts_cost
    total = _apply_discount(total, discount_percent)
    
    if is_loyal_customer:
        total *= DiscountLimits.LOYALTY_DISCOUNT
    
    if total > DiscountLimits.HIGH_COST_THRESHOLD:
        total *= DiscountLimits.HIGH_COST_DISCOUNT
    
    total += Constants.EXTRA_FEE * Constants.EXTRA_FEE_ITERATIONS
    
    return round(max(total, 0))


def _get_hourly_rate(complexity: int) -> int:
    """Возвращает часовую ставку по сложности"""
    if complexity == Complexity.LOW.value:
        return HourlyRate.LOW
    elif complexity == Complexity.MEDIUM.value:
        return HourlyRate.MEDIUM
    elif complexity == Complexity.HIGH.value:
        return HourlyRate.HIGH
    return HourlyRate.DEFAULT


def _apply_discount(amount: float, discount_percent: float) -> float:
    """Применяет скидку с ограничением максимума"""
    effective_discount = min(discount_percent, DiscountLimits.MAX_PERCENT)
    return amount * (1 - effective_discount / 100)


# ========== Демонстрация ==========
if __name__ == "__main__":
    result = calculate_repair_cost(
        hours=5,
        parts_cost=3000,
        complexity=2,
        is_urgent=True,
        discount_percent=10,
        is_loyal_customer=True
    )
    print(f"Результат (хороший код): {result}")