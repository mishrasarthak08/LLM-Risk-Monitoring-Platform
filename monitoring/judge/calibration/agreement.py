from sklearn.metrics import cohen_kappa_score
from typing import List, Dict, Any


def compute_dimension_kappa(human_scores: List[float], judge_scores: List[float], weights: str | None = "linear") -> float:
    """
    Computes Cohen's Kappa score.
    weights='linear' for ordinal 1-5 scales; None for binary 0/1 dims.
    """
    return float(cohen_kappa_score(human_scores, judge_scores, weights=weights))


def calibration_report(human_labels: Dict[str, List[float]], judge_labels: Dict[str, List[float]], thresholds: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    report: Dict[str, Any] = {}
    for dimension, config in thresholds.items():
        if dimension not in human_labels or dimension not in judge_labels:
            continue

        h_scores = human_labels[dimension]
        j_scores = judge_labels[dimension]

        weight = None if config.get("scale_type") == "binary" else "linear"
        kappa = compute_dimension_kappa(h_scores, j_scores, weights=weight)

        report[dimension] = {
            "kappa": kappa,
            "threshold": config["min_kappa"],
            "passed": kappa >= config["min_kappa"]
        }

    report["overall_calibration_status"] = (
        "calibrated" if report and all(d["passed"] for k, d in report.items() if k != "overall_calibration_status")
        else "failed_calibration"
    )

    return report
