"""custom modules

Revision ID: 0003_custom_modules
Revises: 0002_user_ownership
Create Date: 2026-07-03 01:00:00
"""

import sqlalchemy as sa
from alembic import op

revision = "0003_custom_modules"
down_revision = "0002_user_ownership"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "custom_modules",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("custom_modules")
