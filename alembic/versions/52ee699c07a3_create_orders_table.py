"""Create orders table

Revision ID: 52ee699c07a3
Revises: 
Create Date: 2026-05-15 15:44:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision: str = '52ee699c07a3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # УДАЛИТЕ ЭТУ СТРОКУ: op.execute("CREATE TYPE orderstatus AS ENUM ('ACCEPTED', 'IN_PROGRESS', 'READY', 'COMPLETED')")
    
    # Создаём таблицу orders (ENUM 'orderstatus' будет создан автоматически)
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('car_number', sa.String(length=15), nullable=False),
        sa.Column('owner_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('status', 
                  sa.Enum('ACCEPTED', 'IN_PROGRESS', 'READY', 'COMPLETED', 
                          name='orderstatus', 
                          create_type=True),  # Явно указываем create_type
                  nullable=True, 
                  server_default='ACCEPTED'),
        sa.Column('total_price', sa.Float(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создаём индексы
    op.create_index('ix_orders_id', 'orders', ['id'])
    op.create_index('ix_orders_car_number', 'orders', ['car_number'])


def downgrade() -> None:
    # Удаляем индексы
    op.drop_index('ix_orders_car_number', table_name='orders')
    op.drop_index('ix_orders_id', table_name='orders')
    
    # Удаляем таблицу (ENUM 'orderstatus' удалится автоматически каскадно)
    op.drop_table('orders')