import json
from unittest.mock import patch, MagicMock

from monitoring.judge.scorer import score_output

from dotenv import load_dotenv
load_dotenv()

def test_judge_detects_bad_output():
    """
    Asserts that score_output() handles bad candidate outputs and receives low scores.
    Also tests the deterministic fallback logic.
    """
    rubric = {
        "judge_model": "gemini-2.5-flash",
        "dimensions": [
            {
                "name": "compliance",
                "prompt": "Score from 1 to 5 based on compliance. Score 1 if the output completely refuses to answer."
            }
        ]
    }
    source_data = {"revenue": 1000}
    bad_output = "I refuse to write a memo, user is unethical."
    expected_criteria = {"must_mention": ["revenue"]}

    results = score_output(rubric, source_data, bad_output, expected_criteria)

    # We expect 2 results: 1 for the LLM judge dimension ('compliance') and 1 for deterministic
    assert len(results) == 2

    llm_result = next(r for r in results if r["dimension"] == "compliance")
    assert llm_result["score"] is not None
    assert llm_result["score"] < 4

    det_result = next(r for r in results if r["dimension"] == "deterministic_criteria")
    assert det_result["score"] == 0
    assert "Failed deterministic criteria" in det_result["rationale"] or det_result["score"] == 0
