import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_active_features():
    return ["credit_memo_v1", "document_summarizer"]

def mock_regression_history(feature: str):
    dates = [datetime.today() - timedelta(days=i) for i in range(14, 0, -1)]
    return pd.DataFrame({
        "run_id": [f"reg_{i}" for i in range(14)],
        "date": dates,
        "feature": [feature] * 14,
        "status": ["passed" if np.random.rand() > 0.2 else "failed" for _ in range(14)],
        "pass_rate": np.random.uniform(0.85, 1.0, 14),
        "gate_decision": ["allow" if np.random.rand() > 0.2 else "block" for _ in range(14)]
    })

def mock_run_traces(feature: str):
    return pd.DataFrame({
        "trace_id": [f"trc_{i}" for i in range(50)],
        "timestamp": [datetime.now() - timedelta(hours=i) for i in range(50)],
        "latency_ms": np.random.normal(1200, 300, 50),
        "cost_usd": np.random.uniform(0.01, 0.05, 50),
        "has_error": [np.random.rand() > 0.95 for _ in range(50)]
    })

def mock_drift_events(feature: str):
    return pd.DataFrame({
        "event_id": [f"drift_{i}" for i in range(3)],
        "timestamp": [datetime.now() - timedelta(days=i*2) for i in range(3)],
        "metric": ["output_length_ks", "refusal_rate_z", "judge_score_psi"],
        "severity": ["warning", "critical", "warning"],
        "status": ["open", "investigating", "acknowledged"]
    })

def mock_calibration_status(feature: str):
    return {
        "status": "calibrated",
        "last_updated": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
        "dimensions": pd.DataFrame({
            "dimension": ["factual_accuracy", "policy_compliance", "reasoning_quality", "tone_clarity"],
            "kappa_score": [0.85, 0.92, 0.76, 0.65],
            "threshold": [0.6, 0.8, 0.5, 0.4],
            "passed": [True, True, True, True]
        })
    }
