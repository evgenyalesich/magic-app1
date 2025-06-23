"""Add email and stars fields to users table

Revision ID: 5b177383a4fa
Revises: b7d148f80655
Create Date: 2025-06-24 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "5b177383a4fa"
down_revision = "b7d148f80655"
branch_labels = None
depends_on = None


def upgrade():
    # 1) Добавляем email как nullable, чтобы не получить NotNullViolation
    op.add_column(
        "users",
        sa.Column("email", sa.String(length=255), nullable=True),
    )
    # 2) Добавляем поле stars с дефолтным 0
    op.add_column(
        "users",
        sa.Column("stars", sa.Integer(), nullable=False, server_default="0"),
    )
    # Если хотите, чтобы email в будущем стал not-null,
    # раскомментируйте и установите какое-то дефолтное значение:
    #
    # op.execute("UPDATE users SET email = '' WHERE email IS NULL")
    # op.alter_column("users", "email", nullable=False)


def downgrade():
    # Откатываем всё в обратном порядке
    op.drop_column("users", "stars")
    op.drop_column("users", "email")
