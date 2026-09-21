"""Create the initial authenticated ownership schema.

Revision ID: 0001_initial_schema
Revises:
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="analyst"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)

    op.create_table(
        "datasets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("stored_path", sa.Text(), nullable=False),
        sa.Column("rows", sa.Integer(), nullable=False),
        sa.Column("columns", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_datasets_user_id", "datasets", ["user_id"], unique=False)

    op.create_table(
        "analysis_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("dataset_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("analysis_type", sa.String(length=80), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analysis_results_dataset_id", "analysis_results", ["dataset_id"], unique=False)
    op.create_index("ix_analysis_results_user_id", "analysis_results", ["user_id"], unique=False)
    op.create_index("ix_analysis_results_analysis_type", "analysis_results", ["analysis_type"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_analysis_results_analysis_type", table_name="analysis_results")
    op.drop_index("ix_analysis_results_user_id", table_name="analysis_results")
    op.drop_index("ix_analysis_results_dataset_id", table_name="analysis_results")
    op.drop_table("analysis_results")
    op.drop_index("ix_datasets_user_id", table_name="datasets")
    op.drop_table("datasets")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
