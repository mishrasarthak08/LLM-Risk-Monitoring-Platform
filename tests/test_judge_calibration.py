from monitoring.judge.calibration.agreement import compute_dimension_kappa, calibration_report


def test_compute_dimension_kappa_binary():
    human = [1, 1, 1, 0, 0]
    judge = [1, 1, 0, 0, 0]
    # Simple agreement 4/5 (0.8)
    kappa = compute_dimension_kappa(human, judge, weights=None)
    assert 0.5 < kappa < 0.7  # specific kappa value is around 0.583


def test_compute_dimension_kappa_ordinal():
    human = [5, 4, 4, 3, 2]
    judge = [4, 4, 3, 3, 1]
    # Linear weighted kappa should handle the close values well
    kappa = compute_dimension_kappa(human, judge, weights="linear")
    assert kappa > 0.0


def test_calibration_report():
    human_labels = {
        "factual_accuracy": [1, 1, 0, 0],
        "completeness": [1, 1, 1, 0]
    }
    judge_labels = {
        "factual_accuracy": [1, 1, 0, 0],  # Perfect agreement (kappa 1.0)
        "completeness": [1, 0, 0, 1]       # Poor agreement (kappa negative)
    }
    thresholds = {
        "factual_accuracy": {"min_kappa": 0.7, "scale_type": "binary"},
        "completeness": {"min_kappa": 0.7, "scale_type": "binary"}
    }

    report = calibration_report(human_labels, judge_labels, thresholds)

    assert report["factual_accuracy"]["passed"] is True
    assert report["factual_accuracy"]["kappa"] == 1.0

    assert report["completeness"]["passed"] is False
    assert report["overall_calibration_status"] == "failed_calibration"
