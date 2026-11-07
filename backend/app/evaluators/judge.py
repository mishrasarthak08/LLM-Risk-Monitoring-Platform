"""
VERITAS AI — LLM-as-a-Judge Evaluation Engine
Executes isolated dimensional evaluations, structured output parsing, and evidence capture.
"""
import json
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.app.providers.base import BaseLLMProvider
from backend.app.evaluators.deterministic import evaluate_deterministic_criteria


class JudgeScoreOutput(BaseModel):
    score: float = Field(..., description="Numerical score for the dimension")
    rationale: str = Field(..., description="Detailed textual rationale with citations")


def parse_judge_json(raw_text: str) -> Optional[Dict[str, Any]]:
    """Robustly extracts and parses JSON from LLM output."""
    if not raw_text:
        return None
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Search for first { and last }
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return None


async def evaluate_with_judge(
    provider: BaseLLMProvider,
    rubric: Dict[str, Any],
    source_payload: Dict[str, Any],
    candidate_output: str,
    expected_criteria: Optional[Dict[str, Any]] = None,
    model_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Evaluates candidate text across every rubric dimension plus deterministic criteria.
    Each dimension is evaluated in an isolated LLM call to avoid order bias and verbosity bias.
    """
    results: List[Dict[str, Any]] = []

    # 1. First run deterministic assertion check
    det_eval = evaluate_deterministic_criteria(candidate_output, expected_criteria)
    results.append({
        "dimension": "deterministic_criteria",
        "score": det_eval["score"],
        "max_score": 1.0,
        "is_passing": det_eval["passed"],
        "rationale": det_eval["rationale"],
        "evidence": f"Missing: {det_eval['missing_terms']}; Forbidden: {det_eval['forbidden_terms_found']}",
        "raw_response": det_eval
    })

    # 2. Iterate through rubric dimensions
    dimensions = rubric.get("dimensions", [])
    for dim in dimensions:
        dim_name = dim["name"]
        scale = dim.get("scale", [0, 1])
        max_score = float(scale[1])
        dim_prompt = dim["prompt"]

        full_prompt = (
            f"{dim_prompt}\n\n"
            f"SOURCE DATA PAYLOAD (Ground Truth):\n{json.dumps(source_payload, indent=2)}\n\n"
            f"CANDIDATE OUTPUT TO AUDIT:\n{candidate_output}\n\n"
            "Respond in valid JSON only with 'score' and 'rationale' keys."
        )

        gen_result = await provider.generate(
            prompt=full_prompt,
            model_name=model_name,
            temperature=0.0,
            max_tokens=512
        )

        parsed = parse_judge_json(gen_result.text)
        if parsed and "score" in parsed:
            score_val = float(parsed["score"])
            rationale_val = str(parsed.get("rationale", "No rationale provided."))
            is_passing = (score_val >= max_score * 0.7)
            results.append({
                "dimension": dim_name,
                "score": score_val,
                "max_score": max_score,
                "is_passing": is_passing,
                "rationale": rationale_val,
                "evidence": f"Evaluator cited: {rationale_val[:100]}",
                "raw_response": parsed
            })
        else:
            # Fallback error handling
            results.append({
                "dimension": dim_name,
                "score": 0.0,
                "max_score": max_score,
                "is_passing": False,
                "rationale": f"Malformed LLM Judge output: {gen_result.text[:150]}",
                "evidence": None,
                "raw_response": {"raw": gen_result.text, "error": gen_result.error}
            })

    return results

