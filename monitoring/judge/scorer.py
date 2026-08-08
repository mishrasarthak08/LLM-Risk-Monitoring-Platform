import json
import yaml
from typing import Dict, Any, List

from app.client import call_llm


def load_rubric(rubric_path: str) -> Dict[str, Any]:
    with open(rubric_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def _call_llm_judge(prompt: str, model: str) -> str:
    """
    Calls the real LLM judge, enforcing structured JSON output via prompt instructions.
    Uses low temperature for consistent judging.
    """
    judge_config = {
        "model_name": model,
        "temperature": 0.0,
        "max_tokens": 512
    }

    json_prompt = (
        f"{prompt}\n\n"
        "You must evaluate the input and respond with ONLY a valid JSON object. "
        "The JSON object must contain exactly two keys: 'score' (numeric) "
        "and 'rationale' (string). "
        "Do not include markdown blocks or any other text before or after the JSON."
    )

    output, _ = call_llm(json_prompt, judge_config)

    # Sometimes Claude wraps the json in markdown block even if told not to
    output = output.strip()
    if output.startswith("```json"):
        output = output[7:]
    if output.startswith("```"):
        output = output[3:]
    if output.endswith("```"):
        output = output[:-3]

    return output.strip()


from monitoring.judge.checks import check_deterministic_criteria


def score_output(
    rubric: Dict[str, Any],
    source_data: dict,
    candidate_output: str,
    expected_criteria: Dict[str, Any] | None = None
) -> List[Dict[str, Any]]:
    """
    Evaluates a candidate output against all dimensions defined in the rubric.
    Each dimension is scored in a separate LLM call to mitigate position
    and verbosity bias. Also adds a deterministic criteria check.
    """
    results = []

    for dimension in rubric["dimensions"]:
        # We inject the source_data and candidate_output into the dimension's prompt
        prompt = dimension["prompt"]
        prompt += f"\n\nSource data: {json.dumps(source_data)}\n"
        prompt += f"Drafted memo: {candidate_output}\n"

        raw_response = _call_llm_judge(
            prompt, model=rubric.get("judge_model", "default-model")
        )

        try:
            parsed = json.loads(raw_response)
            results.append({
                "dimension": dimension["name"],
                "score": parsed.get("score"),
                "rationale": parsed.get("rationale"),
                "raw_response": raw_response,
                "error": None
            })
        except json.JSONDecodeError as e:
            results.append({
                "dimension": dimension["name"],
                "score": None,
                "rationale": None,
                "raw_response": raw_response,
                "error": str(e)
            })

    # Add deterministic criteria check as an additional signal
    det_result = check_deterministic_criteria(candidate_output, expected_criteria)
    results.append({
        "dimension": "deterministic_criteria",
        "score": 1 if det_result["passed"] else 0,
        "rationale": det_result["rationale"],
        "raw_response": json.dumps(det_result),
        "error": None
    })

    return results
