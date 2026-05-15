"""Add masters table and relationship with orders

Revision ID: 2a3b4c5d6e7f
Revises: 52ee699c07a3
Create Date: 2026-05-15 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '2a3b4c5d6e7f'
down_revision: Union[str, None] = '52ee699c07a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаём таблицу masters
    op.create_table(
        'masters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('specialization', sa.String(length=50), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('hire_date', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Индексы для masters
    op.create_index('ix_masters_specialization', 'masters', ['specialization'])
    
    # Добавляем master_id в orders
    op.add_column('orders', sa.Column('master_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_orders_master_id', 'orders', 'masters', ['master_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_orders_master_id', 'orders', ['master_id'])
    op.create_index('ix_orders_status', 'orders', ['status'])


def downgrade() -> None:
    op.drop_index('ix_orders_status', table_name='orders')
    op.drop_index('ix_orders_master_id', table_name='orders')
    op.drop_constraint('fk_orders_master_id', 'orders', type_='foreignkey')
    op.drop_column('orders', 'master_id')
    op.drop_index('ix_masters_specialization', table_name='masters')
    op.drop_index('ix_masters_id', table_name='masters')
    op.drop_table('masters')