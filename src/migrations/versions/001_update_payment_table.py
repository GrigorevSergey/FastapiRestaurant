"""Update payment table structure

Revision ID: 001_payment_update
Revises: 
Create Date: 2025-01-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_payment_update'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаем схему payments если не существует
    op.execute('CREATE SCHEMA IF NOT EXISTS payments')
    
    # Создаем enum для статусов платежей
    payment_status_enum = postgresql.ENUM(
        'pending', 'completed', 'failed', 'cancelled',
        name='paymentstatus',
        schema='payments'
    )
    # payment_status_enum.create(op.get_bind())  # Удалено, чтобы избежать DuplicateObjectError
    
    # Создаем таблицу payments
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('status', payment_status_enum, nullable=False, server_default='pending'),
        sa.Column('transaction_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),  # <--- добавлено
        sa.ForeignKeyConstraint(['order_id'], ['orders.orders.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='payments'
    )
    
    # Создаем индексы
    op.create_index('ix_payments_id', 'payments', ['id'], schema='payments')
    op.create_index('ix_payments_order_id', 'payments', ['order_id'], schema='payments')


def downgrade() -> None:
    # Удаляем индексы
    op.drop_index('ix_payments_order_id', table_name='payments', schema='payments')
    op.drop_index('ix_payments_id', table_name='payments', schema='payments')
    
    # Удаляем таблицу
    op.drop_table('payments', schema='payments')
    
    # Удаляем enum
    op.execute('DROP TYPE IF EXISTS payments.paymentstatus')
    
    # Удаляем схему (только если пустая)
    op.execute('DROP SCHEMA IF EXISTS payments')