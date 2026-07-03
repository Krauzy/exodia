"""user ownership

Revision ID: 0002_user_ownership
Revises: 0001_initial
Create Date: 2026-07-02 18:00:00
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_user_ownership"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("password_hash", sa.String(length=240), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    with op.batch_alter_table("targets") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.String(length=36), nullable=True))
        batch_op.create_foreign_key("fk_targets_user_id_users", "users", ["user_id"], ["id"], ondelete="CASCADE")
    with op.batch_alter_table("scans") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.String(length=36), nullable=True))
        batch_op.create_foreign_key("fk_scans_user_id_users", "users", ["user_id"], ["id"], ondelete="CASCADE")
    with op.batch_alter_table("reports") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.String(length=36), nullable=True))
        batch_op.create_foreign_key("fk_reports_user_id_users", "users", ["user_id"], ["id"], ondelete="CASCADE")


def downgrade() -> None:
    with op.batch_alter_table("reports") as batch_op:
        batch_op.drop_constraint("fk_reports_user_id_users", type_="foreignkey")
        batch_op.drop_column("user_id")
    with op.batch_alter_table("scans") as batch_op:
        batch_op.drop_constraint("fk_scans_user_id_users", type_="foreignkey")
        batch_op.drop_column("user_id")
    with op.batch_alter_table("targets") as batch_op:
        batch_op.drop_constraint("fk_targets_user_id_users", type_="foreignkey")
        batch_op.drop_column("user_id")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")
