"""Add indices for performance

Revision ID: b4d427538e26
Revises: a3c316427d15
Create Date: 2026-07-20 17:16:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b4d427538e26'
down_revision = 'a3c316427d15'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_index(op.f('ix_run_traces_feature_name'), 'run_traces', ['feature_name'], unique=False)
    op.create_index(op.f('ix_run_traces_created_at'), 'run_traces', ['created_at'], unique=False)
    op.create_index(op.f('ix_judge_scores_run_trace_id'), 'judge_scores', ['run_trace_id'], unique=False)
    op.create_index(op.f('ix_drift_events_feature_name'), 'drift_events', ['feature_name'], unique=False)
    op.create_index(op.f('ix_drift_events_window_start'), 'drift_events', ['window_start'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_drift_events_window_start'), table_name='drift_events')
    op.drop_index(op.f('ix_drift_events_feature_name'), table_name='drift_events')
    op.drop_index(op.f('ix_judge_scores_run_trace_id'), table_name='judge_scores')
    op.drop_index(op.f('ix_run_traces_created_at'), table_name='run_traces')
    op.drop_index(op.f('ix_run_traces_feature_name'), table_name='run_traces')
