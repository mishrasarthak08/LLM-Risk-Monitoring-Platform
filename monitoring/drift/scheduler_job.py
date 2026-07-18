from typing import Any
import yaml
from datetime import datetime
import numpy as np

from monitoring.drift.reference_builder import get_active_reference
from monitoring.drift.detectors import (
    population_stability_index,
    length_distribution_shift,
    refusal_rate_shift
)


def load_thresholds():
    with open("config/thresholds.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config.get("drift_thresholds", {})


def fetch_rolling_window_data(feature_name: str, metric: str, hours: int = 24) -> Any:
    """
    STUB: Fetches the live data stream for the given feature and metric.
    In reality, this would query a database for traces within the last X hours.
    Here we generate mock data to demonstrate the scheduler.
    """
    if metric == "refusal_rate":
        return {"refusals": 150, "total": 1000}  # 15%

    # Mock continuous distributions
    return np.random.normal(loc=100.0, scale=15.0, size=500)


def evaluate_drift(feature_name: str):
    thresholds = load_thresholds()

    # 1. Output Length Drift (KS Test)
    ref_length = get_active_reference(feature_name, "output_length")
    cur_length = fetch_rolling_window_data(feature_name, "output_length")
    if ref_length is not None:
        ks_res = length_distribution_shift(
            np.array(ref_length), np.array(cur_length))
        if ks_res["p_value"] < thresholds.get("output_length_ks_p_value", 0.05):
            print(
                f"[DRIFT DETECTED] output_length shift on {feature_name}! p-value: {ks_res['p_value']:.4e}")

    # 2. Refusal Rate Drift (Two-Proportion Z-Test)
    ref_refusals = get_active_reference(feature_name, "refusal_rate")
    cur_refusals_data = fetch_rolling_window_data(feature_name, "refusal_rate")
    if ref_refusals is not None:
        # the mock returns np.ndarray of 1s and 0s
        z_res = refusal_rate_shift(
            int(sum(ref_refusals)), len(ref_refusals),
            int(cur_refusals_data.sum()), len(cur_refusals_data)
        )
        if z_res["p_value"] < thresholds.get("refusal_rate_z_p_value", 0.05):
            print(
                f"[DRIFT DETECTED] refusal_rate shift on {feature_name}! p-value: {z_res['p_value']:.4e}")

    # 3. Judge Score Distribution Drift (PSI)
    ref_scores = get_active_reference(
        feature_name, "judge_score_fa")  # Factual Accuracy score
    cur_scores = fetch_rolling_window_data(feature_name, "judge_score_fa")
    if ref_scores is not None:
        psi = population_stability_index(
            np.array(ref_scores), np.array(cur_scores))
        if psi > thresholds.get("psi_critical", 0.25):
            print(
                f"[CRITICAL DRIFT] judge_score_fa PSI={psi:.4f} exceeds critical threshold!")
        elif psi > thresholds.get("psi_warning", 0.1):
            print(
                f"[WARNING DRIFT] judge_score_fa PSI={psi:.4f} exceeds warning threshold.")


if __name__ == "__main__":
    # Mock setting up references if none exist so the script runs effectively
    from monitoring.drift.reference_builder import build_reference_distribution
    import os

    if not os.path.exists("monitoring/drift/mock_reference_db.json"):
        print("Initializing mock reference distributions...")
        build_reference_distribution("credit_memo_v1", "output_length", list(
            np.random.normal(100.0, 10.0, 1000)), "t-30d", "t-15d")
        build_reference_distribution("credit_memo_v1", "refusal_rate", {
                                     "refusals": 50, "total": 1000}, "t-30d", "t-15d")  # 5% baseline
        build_reference_distribution("credit_memo_v1", "judge_score_fa", list(
            np.random.normal(0.9, 0.05, 1000)), "t-30d", "t-15d")

    print(
        f"Running drift detection scheduler at {datetime.utcnow().isoformat()}...")
    evaluate_drift("credit_memo_v1")
    print("Drift evaluation complete.")
