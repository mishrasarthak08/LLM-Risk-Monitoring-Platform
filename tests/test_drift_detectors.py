import numpy as np
from monitoring.drift.detectors import (
    population_stability_index,
    length_distribution_shift,
    refusal_rate_shift
)


def test_psi_identical_distributions():
    # Two identical distributions should yield PSI ~ 0
    np.random.seed(42)
    ref = np.random.normal(0.8, 0.1, 1000)
    cur = ref.copy()

    psi = population_stability_index(ref, cur, bins=10)
    assert psi < 0.01  # extremely small


def test_psi_shifted_distribution():
    np.random.seed(42)
    ref = np.random.normal(0.8, 0.1, 1000)
    # Severe shift
    cur = np.random.normal(0.4, 0.1, 1000)

    psi = population_stability_index(ref, cur, bins=10)
    assert psi > 0.25  # critical shift threshold


def test_ks_identical_distributions():
    np.random.seed(42)
    ref = np.random.normal(100.0, 15.0, 500)
    cur = ref.copy()

    res = length_distribution_shift(ref, cur)
    # Identical distributions should not reject the null hypothesis (p-value high)
    assert res["p_value"] > 0.9


def test_ks_shifted_distribution():
    np.random.seed(42)
    ref = np.random.normal(100.0, 15.0, 500)
    cur = np.random.normal(120.0, 15.0, 500)  # mean shifted significantly

    res = length_distribution_shift(ref, cur)
    # Different distributions should reject the null hypothesis (p-value low)
    assert res["p_value"] < 0.05


def test_ztest_refusal_rate_no_shift():
    res = refusal_rate_shift(
        ref_refusals=50, ref_total=1000, cur_refusals=52, cur_total=1000)
    # 5% vs 5.2% should not be significant at N=1000
    assert res["p_value"] > 0.05


def test_ztest_refusal_rate_significant_shift():
    res = refusal_rate_shift(
        ref_refusals=50, ref_total=1000, cur_refusals=150, cur_total=1000)
    # 5% vs 15% should be highly significant at N=1000
    assert res["p_value"] < 0.05
