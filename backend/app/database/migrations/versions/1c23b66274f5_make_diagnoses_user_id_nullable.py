"""make diagnoses.user_id nullable

Revision ID: 1c23b66274f5
Revises: f9d2884f7daf
Create Date: 2026-07-08 09:51:46.051633

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c23b66274f5'
down_revision: Union[str, Sequence[str], None] = 'f9d2884f7daf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("diagnoses", "user_id", nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("diagnoses", "user_id", nullable=False)