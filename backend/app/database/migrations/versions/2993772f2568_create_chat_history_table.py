"""create chat_history table

Revision ID: 2993772f2568
Revises: 1c23b66274f5
Create Date: 2026-07-08 15:16:31.283413

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '2993772f2568'
down_revision: Union[str, Sequence[str], None] = '1c23b66274f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "chat_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("diagnosis_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("diagnoses.id"), nullable=True),
        sa.Column("session_id", sa.String(100), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("reply", sa.Text(), nullable=False),
    )
    op.create_index("ix_chat_history_session_id", "chat_history", ["session_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_chat_history_session_id", table_name="chat_history")
    op.drop_table("chat_history")