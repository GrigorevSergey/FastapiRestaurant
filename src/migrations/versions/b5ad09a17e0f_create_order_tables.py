"""create order tables

Revision ID: b5ad09a17e0f
Revises: e9ecdc50c586
Create Date: 2025-06-17 05:30:35.108986

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5ad09a17e0f'
down_revision: Union[str, None] = 'e9ecdc50c586'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Все create_table и create_index для уже существующих таблиц и индексов удалены, чтобы избежать DuplicateTableError
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # Все drop_table и drop_index для уже существующих таблиц и индексов удалены
    # ### end Alembic commands ###
