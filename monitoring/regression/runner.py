from typing import Dict, Any

from monitoring.golden_set.loader import load_golden_set
from monitoring.judge.scorer import load_rubric, score_output
from monitoring.regression.comparator import compare_case, gate_decision


import yaml
from app.feature.credit_memo import generate_credit_memo

def run_feature_evaluation(prompt_path: str, input_payload: Dict[str, Any]) -> str:
    """
    Runs the LLM feature for the given prompt configuration and input.
    """
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompts = yaml.safe_load(f)
        
    # Create a mock model config for testing
    model_config = {
        "model_name": "gemini-2.5-flash",
        "temperature": 0.0,
        "max_tokens": 1024
    }
    
    # We pass the input_payload to the model prompt directly in a real implementation
    # Here we just inject the payload strings if needed, but our templates don't take it right now.
    # We'll just pass the prompts object and it will run through the traced LLM calls.
    # To use the input payload properly, the credit_memo.py prompts would be formatted with it.
    output = generate_credit_memo(prompts=prompts, model_config=model_config, input_payload=input_payload)
    return output


def run_regression_suite(golden_set_path: str, baseline_prompt_path: str, candidate_prompt_path: str, rubric_path: str, repeats: int = 1) -> Dict[str, Any]:
    cases = load_golden_set(golden_set_path)
    rubric = load_rubric(rubric_path)

    comparisons = []
    case_results = []

    for case in cases:
        # N-repeat stochasticity absorption: run N times, take median score
        # For this prototype we default N=1, but structure allows it.
        baseline_scores = []
        candidate_scores = []

        # We only aggregate the 'factual_accuracy' score for the overall pass/fail in this simplified runner
        # A real implementation would aggregate a unified case score from all dimensions.

        for _ in range(repeats):
            # Run baseline
            base_out = run_feature_evaluation(
                baseline_prompt_path, case.input_payload)
            base_scores = score_output(rubric, case.input_payload, base_out, case.expected_criteria)
            # Find factual accuracy score or default to 0
            base_fa = next((d["score"] for d in base_scores if d["dimension"]
                           == "factual_accuracy" and d["score"] is not None), 0)
            baseline_scores.append(base_fa)

            # Run candidate
            cand_out = run_feature_evaluation(
                candidate_prompt_path, case.input_payload)
            cand_scores = score_output(rubric, case.input_payload, cand_out, case.expected_criteria)
            cand_fa = next((d["score"] for d in cand_scores if d["dimension"]
                           == "factual_accuracy" and d["score"] is not None), 0)
            candidate_scores.append(cand_fa)

        # Median score
        baseline_median = sorted(baseline_scores)[len(baseline_scores) // 2]
        candidate_median = sorted(candidate_scores)[len(candidate_scores) // 2]

        comp = compare_case(str(case.case_hash), case.severity,
                            baseline_median, candidate_median)
        comparisons.append(comp)

        case_results.append({
            "case_hash": case.case_hash,
            "category": case.category,
            "severity": case.severity,
            "baseline_score": baseline_median,
            "candidate_score": candidate_median,
            "delta": comp.delta,
            "verdict": comp.verdict
        })

    gate = gate_decision(comparisons)

    return {
        "gate_decision": gate,
        "case_results": case_results
    }
