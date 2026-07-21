import os
import pandas as pd
import streamlit as st
from datetime import datetime
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from monitoring.db.models import RunTrace, RegressionRun, RegressionCaseResult, DriftEvent, JudgeVersion

@st.cache_resource
def get_engine():
    db_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://dev_user:dev_password@localhost:5432/llm_monitoring_dev")
    return create_engine(db_url, pool_pre_ping=True)

def get_session():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return SessionLocal()

def get_active_features():
    with get_session() as session:
        features = session.query(RunTrace.feature_name).distinct().all()
        return [f[0] for f in features] if features else ["credit_memo_v1"]

def mock_regression_history(feature: str):
    with get_session() as session:
        runs = session.query(RegressionRun).order_by(desc(RegressionRun.started_at)).limit(14).all()
        if not runs:
            return pd.DataFrame(columns=["run_id", "date", "feature", "status", "pass_rate", "gate_decision"])
            
        data = []
        for run in runs:
            results = session.query(RegressionCaseResult).filter(RegressionCaseResult.regression_run_id == run.id).all()
            pass_rate = sum(1 for r in results if r.case_verdict == "pass") / len(results) if results else 0.0
            data.append({
                "run_id": str(run.id),
                "date": run.started_at,
                "feature": feature,
                "status": run.status,
                "pass_rate": pass_rate,
                "gate_decision": run.gate_decision
            })
        return pd.DataFrame(data)

def mock_run_traces(feature: str):
    with get_session() as session:
        traces = session.query(RunTrace).filter(RunTrace.feature_name == feature).order_by(desc(RunTrace.created_at)).limit(50).all()
        if not traces:
            return pd.DataFrame(columns=["trace_id", "timestamp", "latency_ms", "cost_usd", "has_error"])
        return pd.DataFrame([{
            "trace_id": str(t.id),
            "timestamp": t.created_at,
            "latency_ms": t.latency_ms,
            "cost_usd": float(t.cost_usd) if t.cost_usd else 0.0,
            "has_error": t.error is not None
        } for t in traces])

def mock_drift_events(feature: str):
    with get_session() as session:
        events = session.query(DriftEvent).filter(DriftEvent.feature_name == feature).order_by(desc(DriftEvent.window_start)).limit(10).all()
        if not events:
            return pd.DataFrame(columns=["event_id", "timestamp", "metric", "severity", "status"])
        return pd.DataFrame([{
            "event_id": str(e.id),
            "timestamp": e.window_start,
            "metric": e.metric,
            "severity": e.severity,
            "status": "acknowledged" if e.acknowledged_by else "open"
        } for e in events])

def mock_calibration_status(feature: str):
    with get_session() as session:
        judge = session.query(JudgeVersion).order_by(desc(JudgeVersion.created_at)).first()
        if not judge:
            return {
                "status": "pending",
                "last_updated": "never",
                "dimensions": pd.DataFrame(columns=["dimension", "kappa_score", "threshold", "passed"])
            }
        return {
            "status": judge.calibration_status,
            "last_updated": judge.created_at.strftime("%Y-%m-%d") if judge.created_at else "unknown",
            "dimensions": pd.DataFrame({
                "dimension": ["overall_kappa"],
                "kappa_score": [float(judge.last_kappa_score) if judge.last_kappa_score else 0.0],
                "threshold": [0.6],
                "passed": [judge.calibration_status == "calibrated"]
            })
        }
