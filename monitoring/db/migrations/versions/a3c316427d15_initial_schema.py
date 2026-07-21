"""Initial schema

Revision ID: a3c316427d15
Revises:
Create Date: 2026-07-10 14:20:33.734898

"""
import os
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a3c316427d15'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    schema_path = os.path.join(os.path.dirname(__file__), '..', '..', 'schema.sql')
    with open(schema_path, 'r') as f:
        sql = f.read()
    op.execute(sql)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
    DROP TABLE IF EXISTS drift_events CASCADE;
    DROP TABLE IF EXISTS drift_reference_distributions CASCADE;
    DROP TABLE IF EXISTS regression_case_results CASCADE;
    DROP TABLE IF EXISTS regression_runs CASCADE;
    DROP TABLE IF EXISTS judge_scores CASCADE;
    DROP TABLE IF EXISTS judge_versions CASCADE;
    DROP TABLE IF EXISTS run_traces CASCADE;
    DROP TABLE IF EXISTS golden_set_cases CASCADE;
    DROP TABLE IF EXISTS golden_set_versions CASCADE;
    DROP TABLE IF EXISTS model_configs CASCADE;
    DROP TABLE IF EXISTS prompt_versions CASCADE;
    """)
