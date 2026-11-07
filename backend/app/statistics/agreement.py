"""
VERITAS AI — Inter-Annotator Agreement & Evaluator Calibration
Calculates Cohen's Kappa, Weighted Kappa for ordinal scales, and Confusion Matrices.
"""
import numpy as np
from sklearn.metrics import cohen_kappa_score, confusion_matrix
from typing import List, Dict, Any, Optional


def compute_evaluator_agreement(
    human_scores: List[float],
    judge_scores: List[float],
    scale_type: str = "binary",
    min_kappa_threshold: float = 0.70
) -> Dict[str, Any]:
    """
    Computes Cohen's Kappa agreement between human ground truth and automated judge.
    scale_type: 'binary' uses unweighted kappa; 'ordinal' uses linear/quadratic weights.
    """
    n = len(human_scores)
    if n != len(judge_scores):
        raise ValueError(f"Arrays must be equal length. Got {n} vs {len(judge_scores)}.")

    if n < 5:
        return {
            "kappa": 0.0,
            "passed": False,
            "sample_size": n,
            "observed_accuracy": 0.0,
            "warning": f"Insufficient sample size (N={n}, min=5 required)."
        }

    # Binarize or round if float
    h_arr = np.array(human_scores)
    j_arr = np.array(judge_scores)

    if scale_type == "binary":
        weights = None
        # Convert to 0 or 1
        h_labels = (h_arr >= 0.5).astype(int)
        j_labels = (j_arr >= 0.5).astype(int)
    else:
        weights = "linear"
        h_labels = np.round(h_arr).astype(int)
        j_labels = np.round(j_arr).astype(int)

    try:
        kappa = cohen_kappa_score(h_labels, j_labels, weights=weights)
        if np.isnan(kappa):
            kappa = 1.0 if np.array_equal(h_labels, j_labels) else 0.0
    except Exception:
        kappa = 0.0

    kappa = round(float(kappa), 4)
    accuracy = round(float(np.mean(h_labels == j_labels)), 4)

    # Compute confusion matrix
    cm = confusion_matrix(h_labels, j_labels)
    cm_dict = {
        "matrix": cm.tolist(),
        "labels": sorted(list(set(h_labels).union(set(j_labels))))
    }

    return {
        "kappa": kappa,
        "threshold": min_kappa_threshold,
        "passed": bool(kappa >= min_kappa_threshold),
        "observed_accuracy": accuracy,
        "sample_size": n,
        "confusion_matrix": cm_dict,
        "scale_type": scale_type
    }

