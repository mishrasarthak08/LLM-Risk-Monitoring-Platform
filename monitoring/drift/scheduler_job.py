import os
import yaml
import requests
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from monitoring.db.models import RunTrace, JudgeScore, DriftEvent
from monitoring.drift.reference_builder import get_active_reference
from monitoring.drift.detectors import (
    population_stability_index,
    length_distribution_shift,
    refusal_rate_shift
)
from monitoring.utils.json_logger import setup_json_logger

logger = setup_json_logger(__name__)

def get_engine():
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://dev_user:dev_password@localhost:5432/llm_monitoring_dev"
    )
    return create_engine(db_url)

def get_session():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return SessionLocal()

def load_thresholds():
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "config",
        "thresholds.yaml"
    )
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config.get("drift_thresholds", {})

def fetch_rolling_window_data(session, feature_name: str, metric: str, hours: int = 24):
    cutoff = datetime.now() - timedelta(hours=hours)
    
    if metric == "output_length":
        traces = session.query(RunTrace.output_text).filter(
            RunTrace.feature_name == feature_name,
            RunTrace.created_at >= cutoff,
            RunTrace.output_text.isnot(None)
        ).all()
        return np.array([len(t[0]) for t in traces]) if traces else np.array([])

    elif metric == "refusal_rate":
        traces = session.query(RunTrace.error).filter(
            RunTrace.feature_name == feature_name,
            RunTrace.created_at >= cutoff
        ).all()
        # 1 if error (refusal), 0 otherwise
        return np.array(
            [1 if t[0] is not None else 0 for t in traces]
        ) if traces else np.array([])

    elif metric == "judge_score_fa":
        scores = session.query(JudgeScore.score).join(RunTrace).filter(
            RunTrace.feature_name == feature_name,
            RunTrace.created_at >= cutoff,
            JudgeScore.dimension == "factual_accuracy"
        ).all()
        return np.array([float(s[0]) for s in scores]) if scores else np.array([])

    return np.array([])

import uuid


def send_alert(message: str, severity: str):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        logger.info(f"Alert triggered but no webhook URL configured: {message}")
        return
        
    try:
        payload = {"text": f"[{severity.upper()}] {message}"}
        requests.post(webhook_url, json=payload, timeout=5)
    except Exception as e:
        logger.error(f"Failed to send webhook alert: {e}")

def write_drift_event(
    session, feature_name, metric, statistic_value, threshold, severity, sample_size
):
    event = DriftEvent(
        id=uuid.uuid4(),
        feature_name=feature_name,
        metric=metric,
        window_start=datetime.now() - timedelta(hours=24),
        window_end=datetime.now(),
        reference_distribution_id=None,  # In real life, link this properly
        statistic_value=statistic_value,
        threshold=threshold,
        severity=severity,
        sample_size=sample_size
    )
    session.add(event)
    session.commit()

    msg = f"{metric} shift on {feature_name}! stat: {statistic_value:.4f}"
    if severity == "critical":
        logger.critical(f"Drift Event: {msg}")
    else:
        logger.warning(f"Drift Event: {msg}")

    if severity == "critical":
        send_alert(msg, severity)

def evaluate_drift(feature_name: str):
    thresholds = load_thresholds()
    session = get_session()

    try:
        # 1. Output Length Drift (KS Test)
        ref_length = get_active_reference(feature_name, "output_length")
        cur_length = fetch_rolling_window_data(
            session, feature_name, "output_length"
        )
        if ref_length is not None and len(cur_length) > 0:
            ks_res = length_distribution_shift(np.array(ref_length), cur_length)
            threshold = thresholds.get("output_length_ks_p_value", 0.05)
            if ks_res["p_value"] < threshold:
                write_drift_event(
                    session, feature_name, "output_length_ks",
                    ks_res["p_value"], threshold, "warning", len(cur_length)
                )

        # 2. Refusal Rate Drift (Two-Proportion Z-Test)
        ref_refusals = get_active_reference(feature_name, "refusal_rate")
        cur_refusals = fetch_rolling_window_data(
            session, feature_name, "refusal_rate"
        )
        if ref_refusals is not None and len(cur_refusals) > 0:
            # Handle if reference was stored as a dict or array
            ref_sum = (
                ref_refusals.get("refusals", 0)
                if isinstance(ref_refusals, dict)
                else sum(ref_refusals)
            )
            ref_len = (
                ref_refusals.get("total", 1)
                if isinstance(ref_refusals, dict)
                else len(ref_refusals)
            )

            z_res = refusal_rate_shift(
                int(ref_sum), ref_len, int(cur_refusals.sum()), len(cur_refusals)
            )
            threshold = thresholds.get("refusal_rate_z_p_value", 0.05)
            if z_res["p_value"] < threshold:
                write_drift_event(
                    session, feature_name, "refusal_rate_z",
                    z_res["p_value"], threshold, "critical", len(cur_refusals)
                )

        # 3. Judge Score Distribution Drift (PSI)
        ref_scores = get_active_reference(feature_name, "judge_score_fa")
        cur_scores = fetch_rolling_window_data(
            session, feature_name, "judge_score_fa"
        )
        if ref_scores is not None and len(cur_scores) > 0:
            psi = population_stability_index(np.array(ref_scores), cur_scores)
            crit_thresh = thresholds.get("psi_critical", 0.25)
            warn_thresh = thresholds.get("psi_warning", 0.1)

            if psi > crit_thresh:
                write_drift_event(
                    session, feature_name, "judge_score_psi",
                    psi, crit_thresh, "critical", len(cur_scores)
                )
            elif psi > warn_thresh:
                write_drift_event(
                    session, feature_name, "judge_score_psi",
                    psi, warn_thresh, "warning", len(cur_scores)
                )
                
    except Exception as e:
        logger.error(f"Error evaluating drift: {e}")
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    logger.info(
        f"Running drift detection scheduler at {datetime.utcnow().isoformat()}..."
    )
    evaluate_drift("credit_memo_v1")
    logger.info("Drift evaluation complete.")
