import numpy as np
from scipy.stats import ks_2samp
from typing import Dict, Any


def population_stability_index(reference: np.ndarray, current: np.ndarray, bins: int = 10) -> float:
    """
    Standard PSI over a shared binning derived from the reference set.
    Interpretation (documented, versioned in thresholds.yaml):
      < 0.10 : no significant shift
      0.10-0.25 : moderate shift, warning
      > 0.25 : significant shift, critical
    """
    if len(reference) == 0 or len(current) == 0:
        return 0.0

    # Ensure arrays are valid numeric types
    reference = np.asarray(reference, dtype=float)
    current = np.asarray(current, dtype=float)

    # Bin based on quantiles to ensure balanced reference bins
    # Add a tiny noise to prevent identical quantiles dropping bins
    reference_jitter = reference + \
        np.random.uniform(-1e-6, 1e-6, size=reference.shape)
    bin_edges = np.quantile(reference_jitter, np.linspace(0, 1, bins + 1))

    # Catch out-of-range current values
    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf

    # Calculate counts
    ref_counts, _ = np.histogram(reference, bins=bin_edges)
    cur_counts, _ = np.histogram(current, bins=bin_edges)

    # Calculate percentages
    ref_pct = np.clip(ref_counts / len(reference), 1e-4, None)
    cur_pct = np.clip(cur_counts / len(current), 1e-4, None)

    # Calculate PSI
    psi = float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))
    return psi


def length_distribution_shift(reference: np.ndarray, current: np.ndarray) -> Dict[str, Any]:
    """
    Kolmogorov-Smirnov (KS) test for continuous metrics like length or latency.
    """
    if len(reference) == 0 or len(current) == 0:
        return {"ks_statistic": 0.0, "p_value": 1.0}

    statistic, p_value = ks_2samp(reference, current)
    return {"ks_statistic": float(statistic), "p_value": float(p_value)}


def refusal_rate_shift(ref_refusals: int, ref_total: int, cur_refusals: int, cur_total: int) -> Dict[str, Any]:
    """
    Two-proportion z-test for monitoring categorical rates like refusals.
    """
    if ref_total == 0 or cur_total == 0:
        return {"z_statistic": 0.0, "p_value": 1.0}

    from statsmodels.stats.proportion import proportions_ztest

    stat, p_value = proportions_ztest(
        count=[ref_refusals, cur_refusals],
        nobs=[ref_total, cur_total]
    )

    # Handle NaN p_value (e.g. if both proportions are 0 or identically 1.0)
    if np.isnan(p_value):
        p_value = 1.0
        stat = 0.0

    return {"z_statistic": float(stat), "p_value": float(p_value)}
