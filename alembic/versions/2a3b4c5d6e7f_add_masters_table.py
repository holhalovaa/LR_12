"""Add masters table and relationship with orders

Revision ID: 2a3b4c5d6e7f
Revises: 52ee699c07a3
Create Date: 2026-05-15 17:00:00.000000

Это миграция добавляет:
- Таблицу masters (мастера автосервиса)
- Связь один-ко-многим между master и orders
- Индексы для оптимизации запросов
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision: str = '2a3b4c5d6e7f'
down_revision: Union[str, None] = '52ee699c07a3'  # ссылка на предыдущую миграцию
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Применение миграции: создание таблицы masters и связывание с orders
    """
    
    # ============================================
    # 1. Создаём таблицу masters
    # ============================================
    op.create_table(
        'masters',
        sa.Column('id', sa.Integer(), nullable=False, comment='Первичный ключ'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='ФИО мастера'),
        sa.Column('specialization', sa.String(length=50), nullable=False, comment='Специализация (слесарь, электрик, маляр и т.д.)'),
        sa.Column('phone', sa.String(length=20), nullable=True, comment='Контактный телефон'),
        sa.Column('hire_date', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Дата найма'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # ============================================
    # 2. Создаём индексы для таблицы masters
    # ============================================
    # Индекс на specialization (часто фильтруют мастеров по специализации)
    op.create_index('ix_masters_specialization', 'masters', ['specialization'])
    
    # Индекс на id (обычно создаётся автоматически, но явное указание не помешает)
    op.create_index('ix_masters_id', 'masters', ['id'])
    
    # ============================================
    # 3. Добавляем внешний ключ в таблицу orders
    # ============================================
    # Добавляем колонку master_id
    op.add_column('orders', sa.Column('master_id', sa.Integer(), nullable=True))
    
    # Создаём внешний ключ: orders.master_id → masters.id
    # ON DELETE SET NULL: если мастера удалят, у заказов master_id станет NULL
    op.create_foreign_key(
        'fk_orders_master_id',           # имя ограничения
        'orders',                        # таблица, где создаём FK
        'masters',                       # таблица, на которую ссылаемся
        ['master_id'],                   # колонка в orders
        ['id'],                          # колонка в masters
        ondelete='SET NULL'              # поведение при удалении мастера
    )
    
    # ============================================
    # 4. Создаём индексы для таблицы orders
    # ============================================
    # Индекс на master_id (ускоряет JOIN-запросы)
    op.create_index('ix_orders_master_id', 'orders', ['master_id'])
    
    # Индекс на status (часто фильтруют заказы по статусу)
    op.create_index('ix_orders_status', 'orders', ['status'])
    
    # Примечание: индекс на car_number уже создан в первой миграции


def downgrade() -> None:
    """
    Откат миграции: удаление связи и таблицы masters
    """
    
    # ============================================
    # 1. Удаляем индексы из orders
    # ============================================
    op.drop_index('ix_orders_status', table_name='orders')
    op.drop_index('ix_orders_master_id', table_name='orders')
    
    # ============================================
    # 2. Удаляем внешний ключ и колонку
    # ============================================
    op.drop_constraint('fk_orders_master_id', 'orders', type_='foreignkey')
    op.drop_column('orders', 'master_id')
    
    # ============================================
    # 3. Удаляем индексы из masters
    # ============================================
    op.drop_index('ix_masters_specialization', table_name='masters')
    op.drop_index('ix_masters_id', table_name='masters')
    
    # ============================================
    # 4. Удаляем таблицу masters
    # ============================================
    op.drop_table('masters')