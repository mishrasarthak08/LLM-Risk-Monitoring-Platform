"""
VERITAS AI — Continuous Celery Drift Worker Unit Tests
"""
import pytest
from backend.app.worker import celery_app, run_scheduled_drift_analysis


def test_celery_app_configuration():
    assert celery_app.conf.timezone == "UTC"
    assert celery_app.conf.task_track_started is True
    assert "continuous-hourly-drift-monitor" in celery_app.conf.beat_schedule


def test_run_scheduled_drift_analysis_execution():
    # Execute the underlying task function synchronously
    result = run_scheduled_drift_analysis()
    assert result["status"] == "success"
    assert "projects_analyzed" in result
    assert "drift_events_created" in result
    assert isinstance(result["projects_analyzed"], int)

