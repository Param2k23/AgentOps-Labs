"""Add document_id to tasks

Revision ID: 69123479dde7
Revises: 20260722_0001
Create Date: 2026-07-22 20:36:41.221237

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "69123479dde7"
down_revision: Union[str, Sequence[str], None] = "20260722_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.add_column(sa.Column("document_id", sa.Uuid(), nullable=True))
        batch_op.create_index(
            batch_op.f("ix_tasks_document_id"), ["document_id"], unique=False
        )
        batch_op.create_foreign_key(
            "fk_tasks_document_id", "documents", ["document_id"], ["id"], ondelete="CASCADE"
        )

def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.drop_constraint("fk_tasks_document_id", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_tasks_document_id"))
        batch_op.drop_column("document_id")
    # ### end Alembic commands ###
