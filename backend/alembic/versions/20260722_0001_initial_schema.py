"""initial_schema

Revision ID: 20260722_0001
Revises:
Create Date: 2026-07-22 17:00:00.000000

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260722_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------------------------
    # worlds table
    # ---------------------------------------------------------------------------
    op.create_table(
        "worlds",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("industry", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="active", nullable=False),
        sa.Column(
            "metadata",
            sa.JSON().with_variant(postgresql.JSONB(), "postgresql"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_worlds_name", "worlds", ["name"], unique=False)
    op.create_index("ix_worlds_status", "worlds", ["status"], unique=False)

    # ---------------------------------------------------------------------------
    # documents table
    # ---------------------------------------------------------------------------
    op.create_table(
        "documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("world_id", sa.Uuid(), nullable=False),
        sa.Column("filename", sa.String(length=512), nullable=False),
        sa.Column("document_type", sa.String(length=50), nullable=True),
        sa.Column("department", sa.String(length=100), nullable=True),
        sa.Column("storage_path", sa.Text(), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=True),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column(
            "metadata",
            sa.JSON().with_variant(postgresql.JSONB(), "postgresql"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["world_id"], ["worlds.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documents_world_id", "documents", ["world_id"], unique=False)
    op.create_index("ix_documents_document_type", "documents", ["document_type"], unique=False)
    op.create_index("ix_documents_department", "documents", ["department"], unique=False)
    op.create_index("ix_documents_world_document_type", "documents", ["world_id", "document_type"], unique=False)
    op.create_index("ix_documents_world_department", "documents", ["world_id", "department"], unique=False)

    # ---------------------------------------------------------------------------
    # tasks table
    # ---------------------------------------------------------------------------
    op.create_table(
        "tasks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("world_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("department", sa.String(length=100), nullable=True),
        sa.Column("ground_truth", sa.Text(), nullable=True),
        sa.Column("rubric", sa.Text(), nullable=True),
        sa.Column("expected_output", sa.Text(), nullable=True),
        sa.Column(
            "metadata",
            sa.JSON().with_variant(postgresql.JSONB(), "postgresql"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["world_id"], ["worlds.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tasks_world_id", "tasks", ["world_id"], unique=False)
    op.create_index("ix_tasks_difficulty", "tasks", ["difficulty"], unique=False)
    op.create_index("ix_tasks_department", "tasks", ["department"], unique=False)
    op.create_index("ix_tasks_world_difficulty", "tasks", ["world_id", "difficulty"], unique=False)
    op.create_index("ix_tasks_world_department", "tasks", ["world_id", "department"], unique=False)

    # ---------------------------------------------------------------------------
    # evaluation_runs table
    # ---------------------------------------------------------------------------
    op.create_table(
        "evaluation_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("task_id", sa.Uuid(), nullable=False),
        sa.Column("world_id", sa.Uuid(), nullable=False),
        sa.Column("model_name", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="pending", nullable=False),
        sa.Column("accuracy", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("groundedness", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("citation_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("retrieval_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("hallucination_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("tool_success", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("overall_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["world_id"], ["worlds.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_evaluation_runs_task_id", "evaluation_runs", ["task_id"], unique=False)
    op.create_index("ix_evaluation_runs_world_id", "evaluation_runs", ["world_id"], unique=False)
    op.create_index("ix_evaluation_runs_status", "evaluation_runs", ["status"], unique=False)
    op.create_index("ix_evaluation_runs_model_name", "evaluation_runs", ["model_name"], unique=False)
    op.create_index("ix_evaluation_runs_task_model", "evaluation_runs", ["task_id", "model_name"], unique=False)


def downgrade() -> None:
    op.drop_table("evaluation_runs")
    op.drop_table("tasks")
    op.drop_table("documents")
    op.drop_table("worlds")
