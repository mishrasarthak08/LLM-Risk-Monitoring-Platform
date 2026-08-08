import os
import pytest
import numpy as np
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from monitoring.db.models import DriftEvent
from monitoring.drift.scheduler_job import evaluate_drift

@patch("monitoring.drift.scheduler_job.get_active_reference")
@patch("monitoring.drift.scheduler_job.fetch_rolling_window_data")
def test_drift_scheduler_writes_events(mock_fetch, mock_get_ref):
    """
    Asserts that if the current window diverges from the reference distribution,
    the scheduler correctly calculates drift and writes a DriftEvent row.
    """
    feature_name = "test_credit_memo"
    
    # Mock reference to be very long lengths
    def side_effect_get_ref(feat, metric):
        if metric == "output_length":
            return [1000, 1050, 1100, 950, 1020]
        return None
        
    mock_get_ref.side_effect = side_effect_get_ref
    
    # Mock current window to be very short lengths (causes KS test p-value ~0.0)
    def side_effect_fetch(session, feat, metric, hours=24):
        if metric == "output_length":
            return np.array([10, 12, 11, 9, 10])
        return np.array([])
        
    mock_fetch.side_effect = side_effect_fetch
    
    # DB Session
    os.environ["DATABASE_URL"] = "postgresql+psycopg2://dev_user:dev_password@127.0.0.1:5435/llm_monitoring_dev"
    engine = create_engine(os.environ["DATABASE_URL"])
    Session = sessionmaker(bind=engine)
    
    # Clear any previous events for this test feature
    with Session() as session:
        session.query(DriftEvent).filter_by(feature_name=feature_name).delete()
        session.commit()
    
    # Run the scheduler
    evaluate_drift(feature_name)
    
    # Assert
    with Session() as session:
        events = session.query(DriftEvent).filter_by(feature_name=feature_name).all()
        
        # We expect exactly 1 drift event for output_length_ks
        assert len(events) == 1
        event = events[0]
        assert event.metric == "output_length_ks"
        assert event.statistic_value < 0.05  # p_value should be tiny
        assert event.severity == "warning"
