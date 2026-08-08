"""make reference distribution id nullable

Revision ID: da0cb110313e
Revises: b4d427538e26
Create Date: 2026-08-08 23:55:16.955422

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da0cb110313e'
down_revision: Union[str, Sequence[str], None] = 'b4d427538e26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE drift_events ALTER COLUMN reference_distribution_id DROP NOT NULL;")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE drift_events ALTER COLUMN reference_distribution_id SET NOT NULL;")
