"""merge heads

Revision ID: f2715c0d8667
Revises: 001_payment_update, b5ad09a17e0f
Create Date: 2025-06-29 12:11:24.741603

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2715c0d8667'
down_revision: Union[str, None] = ('001_payment_update', 'b5ad09a17e0f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
