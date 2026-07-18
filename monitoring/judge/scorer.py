import json
import yaml
from typing import Dict, Any, List


def load_rubric(rubric_path: str) -> Dict[str, Any]:
    with open(rubric_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _call_llm_judge(prompt: str, model: str) -> str:
    """
    STUB: In a real environment, this calls the LLM API (e.g., Anthropic or OpenAI).
    For now, it returns a mocked successful response.
    """
    # Mock response based on the requested JSON shape
    if "Score 1 if every numeric claim" in prompt:
        return '{"score": 1, "rationale": "All numeric claims match the source data."}'
    elif "Score 1 if the memo remains objective" in prompt:
        return '{"score": 1, "rationale": "No binding language was found."}'
    elif "Score 1 if the memo contains a Summary" in prompt:
        return '{"score": 1, "rationale": "All required sections are present."}'
    elif "Rate the reasoning quality" in prompt:
        return '{"score": 4, "rationale": "Reasoning is solid and references financials."}'
    elif "Rate the tone and clarity" in prompt:
        return '{"score": 5, "rationale": "Highly professional and well-hedged."}'

    return '{"score": 1, "rationale": "Mock generic pass."}'


def score_output(rubric: Dict[str, Any], source_data: dict, candidate_output: str) -> List[Dict[str, Any]]:
    """
    Evaluates a candidate output against all dimensions defined in the rubric.
    Each dimension is scored in a separate LLM call to mitigate position and verbosity bias.
    """
    results = []

    for dimension in rubric["dimensions"]:
        # We inject the source_data and candidate_output into the dimension's prompt
        prompt = dimension["prompt"]
        prompt += f"\n\nSource data: {json.dumps(source_data)}\n"
        prompt += f"Drafted memo: {candidate_output}\n"

        raw_response = _call_llm_judge(
            prompt, model=rubric.get("judge_model", "default-model"))

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

    return results
