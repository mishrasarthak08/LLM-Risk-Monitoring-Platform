"""
VERITAS AI — Test Suite: Statistical Methods & Hypothesis Testing
Verifies Wilcoxon test, Cliff's Delta, PSI, KS test, 2-proportion Z test, and Cohen's Kappa.
"""
import numpy as np
import pytest

from backend.app.statistics.wilcoxon import compute_paired_comparison
from backend.app.statistics.drift_detectors import (
    population_stability_index,
    kolmogorov_smirnov_shift,
    two_proportion_z_shift
)
from backend.app.statistics.agreement import compute_evaluator_agreement


def test_wilcoxon_paired_comparison_identical():
    # If baseline and candidate are identical, Wilcoxon should report p=1.0 and delta=0
    baseline = [0.95, 0.90, 0.85, 1.0, 0.75, 0.80, 0.90, 0.88, 0.92, 0.86]
    candidate = [0.95, 0.90, 0.85, 1.0, 0.75, 0.80, 0.90, 0.88, 0.92, 0.86]

    res = compute_paired_comparison(baseline, candidate)
    assert res["p_value"] == 1.0
    assert res["mean_delta"] == 0.0
    assert res["effect_size"] == 0.0
    assert res["significant_regression"] is False


def test_wilcoxon_paired_comparison_significant_regression():
    # Candidate scores are significantly worse than baseline
    baseline = [1.0, 1.0, 0.95, 0.90, 1.0, 0.85, 0.90, 0.95, 1.0, 0.90, 0.95, 1.0]
    candidate = [0.4, 0.5, 0.45, 0.50, 0.35, 0.40, 0.50, 0.45, 0.30, 0.40, 0.50, 0.35]

    res = compute_paired_comparison(baseline, candidate, p_value_threshold=0.05)
    assert res["p_value"] < 0.01
    assert res["mean_delta"] < -0.4
    assert res["effect_size"] < 0.0  # Cliff's delta negative
    assert res["significant_regression"] is True


def test_psi_calculation_stability():
    # Identical distributions should have near zero PSI
    reference = np.random.normal(loc=1.0, scale=0.1, size=100)
    current = reference.copy()

    res = population_stability_index(reference, current, min_sample_size=20)
    assert res["psi"] < 0.05
    assert res["severity"] == "INFO"

    # Heavily shifted distribution should trigger CRITICAL severity (PSI >= 0.25)
    shifted_current = np.random.normal(loc=3.5, scale=0.5, size=100)
    shift_res = population_stability_index(reference, shifted_current, min_sample_size=20)
    assert shift_res["psi"] >= 0.25
    assert shift_res["severity"] == "CRITICAL"


def test_kolmogorov_smirnov_shift():
    ref_lengths = [500 + np.random.randint(-20, 20) for _ in range(50)]
    cur_lengths_shifted = [900 + np.random.randint(-20, 20) for _ in range(50)]

    res = kolmogorov_smirnov_shift(ref_lengths, cur_lengths_shifted, min_sample_size=30)
    assert res["is_drift"] is True
    assert res["p_value"] < 0.01
    assert res["severity"] == "WARNING"


def test_two_proportion_z_shift():
    # Baseline refusal rate: 1 in 100 (1%)
    # Current refusal rate: 20 in 100 (20%) -> massive spike
    res = two_proportion_z_shift(ref_successes=1, ref_total=100, cur_successes=20, cur_total=100)
    assert res["is_drift"] is True
    assert res["p_value"] < 0.01
    assert res["severity"] == "CRITICAL"


def test_cohen_kappa_evaluator_agreement():
    # High agreement
    human = [1, 1, 0, 1, 0, 1, 1, 0, 1, 0]
    judge = [1, 1, 0, 1, 0, 1, 1, 0, 1, 0]

    res = compute_evaluator_agreement(human, judge, scale_type="binary", min_kappa_threshold=0.70)
    assert res["kappa"] == 1.0
    assert res["passed"] is True
    assert res["observed_accuracy"] == 1.0

    # Low agreement
    bad_judge = [0, 0, 1, 0, 1, 0, 0, 1, 0, 1]
    bad_res = compute_evaluator_agreement(human, bad_judge, scale_type="binary", min_kappa_threshold=0.70)
    assert bad_res["kappa"] <= 0.0
    assert bad_res["passed"] is False

