"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-01 20:00:00
"""

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )
    op.create_table(
        "targets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("target_type", sa.String(length=16), nullable=False),
        sa.Column("value", sa.String(length=512), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("authorization_scope", sa.Text(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "scans",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("target_id", sa.String(length=36), nullable=False),
        sa.Column("modules", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_module", sa.String(length=120), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("authorization_confirmed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["target_id"], ["targets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "findings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scan_id", sa.String(length=36), nullable=False),
        sa.Column("module_id", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "module_execution_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("scan_id", sa.String(length=36), nullable=False),
        sa.Column("module_id", sa.String(length=120), nullable=True),
        sa.Column("event_type", sa.String(length=48), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "reports",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scan_id", sa.String(length=36), nullable=False),
        sa.Column("format", sa.String(length=24), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("reports")
    op.drop_table("module_execution_logs")
    op.drop_table("findings")
    op.drop_table("scans")
    op.drop_table("targets")
    op.drop_table("app_settings")

