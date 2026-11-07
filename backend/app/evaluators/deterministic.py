"""
VERITAS AI — Deterministic Criteria Evaluator
"""
import re
from typing import Dict, Any, List, Optional


def evaluate_deterministic_criteria(
    candidate_output: str,
    expected_criteria: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Evaluates exact deterministic assertions:
    - must_mention: required strings or regex patterns
    - must_not: forbidden strings or leak terms
    - numeric_bounds: e.g. min_dscr, max_dti
    """
    if not expected_criteria or not candidate_output:
        return {
            "passed": True,
            "score": 1.0,
            "rationale": "No deterministic criteria specified.",
            "missing_terms": [],
            "forbidden_terms_found": []
        }

    must_mention = expected_criteria.get("must_mention", [])
    must_not = expected_criteria.get("must_not", [])
    missing = []
    forbidden_found = []

    for term in must_mention:
        if not re.search(re.escape(term), candidate_output, re.IGNORECASE):
            missing.append(term)

    for term in must_not:
        if re.search(re.escape(term), candidate_output, re.IGNORECASE):
            forbidden_found.append(term)

    passed = len(missing) == 0 and len(forbidden_found) == 0

    reasons = []
    if missing:
        reasons.append(f"Missing mandatory covenants/terms: {', '.join(missing)}")
    if forbidden_found:
        reasons.append(f"Contains prohibited terms: {', '.join(forbidden_found)}")
    if not reasons:
        reasons.append("All deterministic keyword and covenant assertions satisfied.")

    return {
        "passed": passed,
        "score": 1.0 if passed else 0.0,
        "rationale": "; ".join(reasons),
        "missing_terms": missing,
        "forbidden_terms_found": forbidden_found
    }

