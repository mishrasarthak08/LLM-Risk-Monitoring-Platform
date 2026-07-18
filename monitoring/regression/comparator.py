from scipy.stats import wilcoxon
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class CaseComparison:
    case_id: str
    severity: str
    baseline_score: float
    candidate_score: float
    delta: float
    verdict: str  # improved | unchanged | regressed | newly_failing | newly_passing


def compare_case(case_id: str, severity: str, baseline_score: float, candidate_score: float, pass_threshold: float = 0.7) -> CaseComparison:
    delta = candidate_score - baseline_score
    was_passing = baseline_score >= pass_threshold
    now_passing = candidate_score >= pass_threshold

    if was_passing and not now_passing:
        verdict = "newly_failing"
    elif not was_passing and now_passing:
        verdict = "newly_passing"
    elif abs(delta) < 0.02:
        verdict = "unchanged"
    else:
        verdict = "improved" if delta > 0 else "regressed"

    return CaseComparison(case_id, severity, baseline_score, candidate_score, delta, verdict)


def gate_decision(comparisons: List[CaseComparison]) -> Dict[str, Any]:
    blocking_newly_failing = [
        c for c in comparisons
        if c.severity == "blocking" and c.verdict == "newly_failing"
    ]

    major_newly_failing = [
        c for c in comparisons
        if c.severity == "major" and c.verdict == "newly_failing"
    ]

    scores_baseline = [c.baseline_score for c in comparisons]
    scores_candidate = [c.candidate_score for c in comparisons]

    # Paired Wilcoxon signed-rank test
    # If all differences are zero, wilcoxon raises ValueError, so we handle it.
    if all(b == c for b, c in zip(scores_baseline, scores_candidate)):
        p_value = 1.0
    else:
        try:
            stat, p_value = wilcoxon(scores_baseline, scores_candidate)
        except ValueError:
            p_value = 1.0

    if blocking_newly_failing:
        return {
            "decision": "block",
            "reason": f"{len(blocking_newly_failing)} blocking-severity case(s) newly failing",
            "p_value": p_value
        }

    if len(major_newly_failing) >= 3:
        return {
            "decision": "block",
            "reason": f"{len(major_newly_failing)} major-severity cases newly failing (threshold: 3)",
            "p_value": p_value
        }

    if p_value < 0.05 and sum(c.delta for c in comparisons) < 0:
        return {
            "decision": "allow_with_warning",
            "reason": "Statistically significant net score decline, no individual blocking failures",
            "p_value": p_value
        }

    return {"decision": "allow", "p_value": p_value}
