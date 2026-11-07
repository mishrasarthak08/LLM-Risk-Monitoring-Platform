"""
VERITAS AI — Continuous Statistical Drift Detectors
Includes Population Stability Index (PSI), Kolmogorov-Smirnov, and Two-Proportion Z tests.
"""
import numpy as np
from scipy.stats import ks_2samp
from typing import Dict, Any, List, Union


def population_stability_index(
    reference: Union[List[float], np.ndarray],
    current: Union[List[float], np.ndarray],
    bins: int = 10,
    min_sample_size: int = 20
) -> Dict[str, Any]:
    """
    Computes Population Stability Index (PSI) with quantile-based reference bins.
    Interpretation:
      PSI < 0.10: Stable / No significant shift
      0.10 <= PSI < 0.25: Moderate shift (Warning)
      PSI >= 0.25: Significant shift (Critical degradation)
    """
    ref_arr = np.asarray(reference, dtype=float)
    cur_arr = np.asarray(current, dtype=float)

    if len(ref_arr) < min_sample_size or len(cur_arr) < min_sample_size:
        return {
            "psi": 0.0,
            "severity": "INFO",
            "sample_size": len(cur_arr),
            "ref_sample_size": len(ref_arr),
            "warning": f"Insufficient sample size (cur={len(cur_arr)}, ref={len(ref_arr)}, min={min_sample_size})."
        }

    # Add minute jitter to reference to avoid duplicate bin edges on low-variance distributions
    ref_jitter = ref_arr + np.random.uniform(-1e-6, 1e-6, size=ref_arr.shape)
    bin_edges = np.quantile(ref_jitter, np.linspace(0, 1, bins + 1))
    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf

    ref_counts, _ = np.histogram(ref_arr, bins=bin_edges)
    cur_counts, _ = np.histogram(cur_arr, bins=bin_edges)

    # Convert to percentages with minimum epsilon smoothing (0.0001)
    ref_pct = np.clip(ref_counts / len(ref_arr), 1e-4, None)
    cur_pct = np.clip(cur_counts / len(cur_arr), 1e-4, None)

    psi_val = float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))
    psi_val = max(0.0, round(psi_val, 4))

    if psi_val >= 0.25:
        severity = "CRITICAL"
    elif psi_val >= 0.10:
        severity = "WARNING"
    else:
        severity = "INFO"

    return {
        "psi": psi_val,
        "severity": severity,
        "sample_size": len(cur_arr),
        "ref_sample_size": len(ref_arr),
        "warning": None
    }


def kolmogorov_smirnov_shift(
    reference: Union[List[float], np.ndarray],
    current: Union[List[float], np.ndarray],
    p_value_threshold: float = 0.05,
    min_sample_size: int = 30
) -> Dict[str, Any]:
    """
    Two-sample Kolmogorov-Smirnov test for continuous variables (output length, latency).
    """
    ref_arr = np.asarray(reference, dtype=float)
    cur_arr = np.asarray(current, dtype=float)

    if len(ref_arr) < min_sample_size or len(cur_arr) < min_sample_size:
        return {
            "ks_statistic": 0.0,
            "p_value": 1.0,
            "severity": "INFO",
            "is_drift": False,
            "sample_size": len(cur_arr),
            "warning": f"Sample size below recommended minimum (N={min_sample_size})."
        }

    stat, p_val = ks_2samp(ref_arr, cur_arr)
    stat = round(float(stat), 4)
    p_val = round(float(p_val), 4)
    is_drift = bool(p_val < p_value_threshold)

    return {
        "ks_statistic": stat,
        "p_value": p_val,
        "severity": "WARNING" if is_drift else "INFO",
        "is_drift": is_drift,
        "sample_size": len(cur_arr),
        "ref_sample_size": len(ref_arr),
        "warning": None
    }


def two_proportion_z_shift(
    ref_successes: int,
    ref_total: int,
    cur_successes: int,
    cur_total: int,
    p_value_threshold: float = 0.05
) -> Dict[str, Any]:
    """
    Two-proportion Z-test for monitoring categorical rates (e.g. refusal rate, error rate).
    """
    if ref_total == 0 or cur_total == 0:
        return {
            "z_statistic": 0.0,
            "p_value": 1.0,
            "severity": "INFO",
            "is_drift": False,
            "cur_rate": 0.0,
            "ref_rate": 0.0,
            "warning": "Empty sample"
        }

    from statsmodels.stats.proportion import proportions_ztest

    ref_rate = ref_successes / ref_total
    cur_rate = cur_successes / cur_total

    try:
        stat, p_val = proportions_ztest(
            count=[cur_successes, ref_successes],
            nobs=[cur_total, ref_total]
        )
        if np.isnan(p_val):
            p_val = 1.0
            stat = 0.0
    except Exception as e:
        p_val = 1.0
        stat = 0.0

    stat = round(float(stat), 4)
    p_val = round(float(p_val), 4)
    is_drift = bool(p_val < p_value_threshold and cur_rate > ref_rate)

    severity = "CRITICAL" if is_drift and (cur_rate - ref_rate >= 0.05) else ("WARNING" if is_drift else "INFO")

    return {
        "z_statistic": stat,
        "p_value": p_val,
        "cur_rate": round(cur_rate, 4),
        "ref_rate": round(ref_rate, 4),
        "rate_delta": round(cur_rate - ref_rate, 4),
        "severity": severity,
        "is_drift": is_drift,
        "cur_total": cur_total,
        "ref_total": ref_total
    }

