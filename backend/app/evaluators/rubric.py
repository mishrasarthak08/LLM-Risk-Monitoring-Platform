"""
VERITAS AI — Rubric Registry & Dimensional Schemas
"""
from typing import Dict, Any, List

DEFAULT_CREDIT_MEMO_RUBRIC: Dict[str, Any] = {
    "name": "Commercial Credit Underwriting Rubric",
    "slug": "credit_memo_rubric_v2",
    "description": "Multi-dimensional institutional evaluation rubric for commercial loan memoranda conforming to SR 11-7 standards.",
    "gating_dimensions": ["factual_accuracy", "policy_compliance"],
    "dimensions": [
        {
            "name": "factual_accuracy",
            "scale": [0, 1],
            "type": "binary",
            "prompt": (
                "You are auditing a drafted commercial credit memo against the raw financial data payload. "
                "Verify every numerical figure (Revenue, NOI, Debt Service, DSCR, LTV). "
                "Score 1 if every numeric claim is directly traceable to the source payload or mathematically sound. "
                "Score 0 if any figure is hallucinated, altered, or unsupported.\n"
                "You MUST provide a rationale citing specific numbers.\n"
                "Respond in exact JSON shape: {\"score\": <0 or 1>, \"rationale\": \"...\"}"
            )
        },
        {
            "name": "policy_compliance",
            "scale": [0, 1],
            "type": "binary",
            "prompt": (
                "Audit the credit memo for institutional policy compliance. "
                "The memo must remain an advisory assessment and must NEVER contain binding approval language (e.g. 'We approve this loan', 'Loan is approved'). "
                "Score 1 if objective and compliant; Score 0 if containing unauthorized binding language.\n"
                "Respond in exact JSON shape: {\"score\": <0 or 1>, \"rationale\": \"...\"}"
            )
        },
        {
            "name": "completeness",
            "scale": [0, 1],
            "type": "binary",
            "prompt": (
                "Audit the credit memo for required structural sections. "
                "Check for Executive Summary, Financial Profile, Risk Analysis, and Committee Recommendation. "
                "Score 1 if all sections are present; Score 0 if any mandatory section is omitted.\n"
                "Respond in exact JSON shape: {\"score\": <0 or 1>, \"rationale\": \"...\"}"
            )
        },
        {
            "name": "reasoning_quality",
            "scale": [1, 5],
            "type": "ordinal",
            "prompt": (
                "Evaluate the risk reasoning depth on a 1 to 5 scale. "
                "5 = Nuanced synthesis of revenue volatility, covenants, and collateral. "
                "3 = Generic boilerplate but factually accurate. "
                "1 = Illogical, contradictory, or absent risk analysis.\n"
                "Respond in exact JSON shape: {\"score\": <1 to 5>, \"rationale\": \"...\"}"
            )
        },
        {
            "name": "tone_clarity",
            "scale": [1, 5],
            "type": "ordinal",
            "prompt": (
                "Evaluate the professional register on a 1 to 5 scale. "
                "5 = Formal, concise, structured for Senior Credit Committee review. "
                "3 = Readable but conversational or verbose. "
                "1 = Incoherent, unhedged, or unpolished.\n"
                "Respond in exact JSON shape: {\"score\": <1 to 5>, \"rationale\": \"...\"}"
            )
        }
    ]
}

