"""drop tg_hash from users

Revision ID: 05fd5360d17f
Revises: 61feae71b805
Create Date: 2025-07-12 22:07:07.773282

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05fd5360d17f'
down_revision: Union[str, None] = '61feae71b805'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
