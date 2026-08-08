import re
from typing import List, Dict, Any

def check_deterministic_criteria(
    candidate_output: str,
    expected_criteria: Dict[str, List[str]] | None
) -> Dict[str, Any]:
    """
    Deterministically checks if the candidate_output mentions required terms
    and avoids forbidden terms.
    """
    if not expected_criteria:
        return {"passed": True, "rationale": "No deterministic criteria provided."}

    must_mention = expected_criteria.get("must_mention", [])
    must_not = expected_criteria.get("must_not", [])

    missing = []
    for term in must_mention:
        # Simple substring or regex match (case-insensitive for robustness)
        if not re.search(re.escape(term), candidate_output, re.IGNORECASE):
            missing.append(term)

    forbidden_found = []
    for term in must_not:
        if re.search(re.escape(term), candidate_output, re.IGNORECASE):
            forbidden_found.append(term)

    if missing or forbidden_found:
        rationale = []
        if missing:
            rationale.append(f"Missing required terms: {', '.join(missing)}")
        if forbidden_found:
            rationale.append(f"Found forbidden terms: {', '.join(forbidden_found)}")

        return {
            "passed": False,
            "rationale": "; ".join(rationale)
        }

    return {
        "passed": True,
        "rationale": "All deterministic criteria met."
    }
