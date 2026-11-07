"""
VERITAS AI — Statistical Regression & Paired Comparison Engine
Implements paired Wilcoxon signed-rank test, Rank-Biserial effect sizes, and Cliff's Delta.
"""
import numpy as np
from scipy.stats import wilcoxon
from typing import List, Dict, Any, Tuple


def compute_paired_comparison(
    baseline_scores: List[float],
    candidate_scores: List[float],
    p_value_threshold: float = 0.05
) -> Dict[str, Any]:
    """
    Executes paired statistical analysis between baseline and candidate scores.
    Handles low sample sizes, zero variances, and calculates effect sizes.
    """
    n = len(baseline_scores)
    if n != len(candidate_scores):
        raise ValueError(f"Score vectors must be equal length. Got {n} vs {len(candidate_scores)}.")

    if n == 0:
        return {
            "p_value": 1.0,
            "effect_size": 0.0,
            "statistic": 0.0,
            "sample_size": 0,
            "significant_regression": False,
            "warning": "Empty sample"
        }

    diffs = np.array(candidate_scores) - np.array(baseline_scores)
    mean_delta = float(np.mean(diffs))
    median_delta = float(np.median(diffs))

    improved_count = int(np.sum(diffs > 0.01))
    regressed_count = int(np.sum(diffs < -0.01))
    unchanged_count = int(np.sum(np.abs(diffs) <= 0.01))

    # Calculate Cliff's Delta
    greater = sum(1 for c in candidate_scores for b in baseline_scores if c > b)
    lesser = sum(1 for c in candidate_scores for b in baseline_scores if c < b)
    cliffs_delta = float((greater - lesser) / (n * n)) if n > 0 else 0.0

    # If all differences are zero, Wilcoxon raises ValueError
    non_zero_diffs = diffs[diffs != 0]
    warning = None

    if len(non_zero_diffs) == 0:
        return {
            "p_value": 1.0,
            "effect_size": 0.0,
            "statistic": 0.0,
            "mean_delta": 0.0,
            "median_delta": 0.0,
            "sample_size": n,
            "improved_count": 0,
            "regressed_count": 0,
            "unchanged_count": n,
            "significant_regression": False,
            "warning": "All paired scores are identical."
        }

    if n < 10:
        warning = f"Sample size (N={n}) is below recommended power threshold (N>=10) for Wilcoxon test."

    try:
        res = wilcoxon(baseline_scores, candidate_scores, alternative="two-sided")
        p_val = float(res.pvalue)
        stat = float(res.statistic)
    except Exception as e:
        p_val = 1.0
        stat = 0.0
        warning = f"Wilcoxon calculation fallback: {str(e)}"

    # Rank-Biserial correlation r = 1 - (2*W) / (n*(n+1)/2)
    # where W is the test statistic
    total_ranks = n * (n + 1) / 2.0
    rank_biserial = float(1.0 - (2.0 * stat / total_ranks)) if total_ranks > 0 else 0.0

    significant_regression = (p_val < p_value_threshold) and (mean_delta < 0)

    return {
        "p_value": round(p_val, 4),
        "statistic": round(stat, 4),
        "rank_biserial_r": round(rank_biserial, 4),
        "cliffs_delta": round(cliffs_delta, 4),
        "effect_size": round(cliffs_delta, 4),
        "mean_delta": round(mean_delta, 4),
        "median_delta": round(median_delta, 4),
        "sample_size": n,
        "improved_count": improved_count,
        "regressed_count": regressed_count,
        "unchanged_count": unchanged_count,
        "significant_regression": significant_regression,
        "warning": warning
    }

