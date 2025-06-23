"""Add email and hashed_password to userss

Revision ID: 055a80af4dba
Revises: dcd5fd10b245
Create Date: 2025-06-24 01:25:49.571144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '055a80af4dba'
down_revision: Union[str, None] = 'dcd5fd10b245'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # добавляем is_active с дефолтом True (или False, как вам нужно) и NOT NULL
    op.add_column(
        'users',
        sa.Column(
            'is_active',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('TRUE')  # или 'FALSE'
        )
    )
    # сразу убираем server_default, если не хотим держать его в модели
    op.alter_column('users', 'is_active', server_default=None)


def downgrade():
    op.drop_column('users', 'is_active')
