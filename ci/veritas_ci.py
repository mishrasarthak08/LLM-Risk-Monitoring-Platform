#!/usr/bin/env python3
"""
VERITAS AI — Headless CI/CD Evaluation Gatekeeper CLI
Used in GitHub Actions to evaluate prompt PRs, compute Wilcoxon statistics, and enforce gate policies.
Exits with 0 (ALLOW / ALLOW_WITH_WARNING) or 1 (BLOCK).
"""
import sys
import os
import argparse
import asyncio
import json
import yaml

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.providers.factory import get_llm_provider
from backend.app.evaluators.judge import evaluate_with_judge
from backend.app.evaluators.rubric import DEFAULT_CREDIT_MEMO_RUBRIC
from backend.app.statistics.wilcoxon import compute_paired_comparison


async def run_ci_gate(
    baseline_prompt_path: str,
    candidate_prompt_path: str,
    dataset_path: str,
    rubric_path: str = None
) -> int:
    print("=" * 70)
    print("VERITAS AI — Automated CI Regression Gate")
    print("=" * 70)

    # Load baseline prompt
    with open(baseline_prompt_path, "r", encoding="utf-8") as f:
        base_content = f.read()

    # Load candidate prompt
    with open(candidate_prompt_path, "r", encoding="utf-8") as f:
        cand_content = f.read()

    # Load benchmark dataset cases (JSONL)
    cases = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))

    print(f"Loaded {len(cases)} benchmark test cases from {dataset_path}")
    print(f"Comparing Baseline ({os.path.basename(baseline_prompt_path)}) vs Candidate ({os.path.basename(candidate_prompt_path)})")

    provider = get_llm_provider()
    rubric = DEFAULT_CREDIT_MEMO_RUBRIC

    baseline_scores = []
    candidate_scores = []
    blocking_newly_failing = 0
    major_newly_failing = 0
    case_summaries = []

    for idx, case in enumerate(cases, start=1):
        payload = case.get("input_payload", {})
        severity = case.get("severity", "major")
        criteria = case.get("expected_criteria")

        # 1. Evaluate Baseline
        base_gen = await provider.generate(prompt=f"{base_content}\n\nPayload:\n{json.dumps(payload)}")
        base_evals = await evaluate_with_judge(
            provider=provider,
            rubric=rubric,
            source_payload=payload,
            candidate_output=base_gen.text,
            expected_criteria=criteria
        )
        base_score = next((e["score"] for e in base_evals if e["dimension"] == "factual_accuracy"), 1.0)
        baseline_scores.append(float(base_score))

        # 2. Evaluate Candidate
        cand_gen = await provider.generate(prompt=f"{cand_content}\n\nPayload:\n{json.dumps(payload)}")
        cand_evals = await evaluate_with_judge(
            provider=provider,
            rubric=rubric,
            source_payload=payload,
            candidate_output=cand_gen.text,
            expected_criteria=criteria
        )
        cand_score = next((e["score"] for e in cand_evals if e["dimension"] == "factual_accuracy"), 1.0)
        candidate_scores.append(float(cand_score))

        # Check newly failing
        was_pass = base_score >= 0.7
        now_pass = cand_score >= 0.7
        verdict = "PASS" if now_pass else "FAIL"

        if was_pass and not now_pass:
            verdict = "NEWLY_FAILING"
            if severity == "blocking":
                blocking_newly_failing += 1
            elif severity == "major":
                major_newly_failing += 1

        case_summaries.append({
            "case_id": idx,
            "category": case.get("category"),
            "severity": severity,
            "base_score": base_score,
            "cand_score": cand_score,
            "verdict": verdict
        })

    # Statistical Analysis
    stats = compute_paired_comparison(baseline_scores, candidate_scores)

    print("\n" + "-" * 70)
    print("STATISTICAL EVALUATION SUMMARY")
    print("-" * 70)
    print(f"Total Test Cases:            {len(cases)}")
    print(f"Newly Failing (Blocking):    {blocking_newly_failing}")
    print(f"Newly Failing (Major):       {major_newly_failing}")
    print(f"Wilcoxon Signed-Rank p-val:  {stats['p_value']}")
    print(f"Cliff's Delta Effect Size:   {stats['effect_size']}")
    print(f"Mean Delta:                  {stats['mean_delta']:+.4f}")

    print("\nCase-by-Case Breakdown:")
    for cs in case_summaries:
        status_flag = "❌" if "FAIL" in cs["verdict"] else "✅"
        print(f" {status_flag} Case #{cs['case_id']} [{cs['severity'].upper()}] {cs['category']}: base={cs['base_score']:.1f}, cand={cs['cand_score']:.1f} -> {cs['verdict']}")

    print("\n" + "=" * 70)
    if blocking_newly_failing > 0:
        print("🛑 CI GATE DECISION: BLOCKED")
        print(f"Reason: {blocking_newly_failing} blocking-severity test case(s) newly failed.")
        print("=" * 70)
        return 1
    elif major_newly_failing >= 3:
        print("🛑 CI GATE DECISION: BLOCKED")
        print(f"Reason: {major_newly_failing} major-severity test cases newly failed (threshold: 3).")
        print("=" * 70)
        return 1
    elif stats["significant_regression"]:
        print("⚠️ CI GATE DECISION: ALLOW WITH WARNING")
        print("Reason: Statistically significant net score decline, but zero blocking failures.")
        print("=" * 70)
        return 0
    else:
        print("✅ CI GATE DECISION: ALLOW")
        print("Reason: All critical institutional covenants and statistical parity checks satisfied.")
        print("=" * 70)
        return 0


def main():
    parser = argparse.ArgumentParser(description="VERITAS AI Headless CI Regression Gate")
    parser.add_argument("--baseline", required=True, help="Path to baseline prompt file")
    parser.add_argument("--candidate", required=True, help="Path to candidate prompt file")
    parser.add_argument("--dataset", required=True, help="Path to benchmark JSONL dataset")
    parser.add_argument("--rubric", required=False, help="Path to evaluation rubric YAML")

    args = parser.parse_args()

    exit_code = asyncio.run(run_ci_gate(
        baseline_prompt_path=args.baseline,
        candidate_prompt_path=args.candidate,
        dataset_path=args.dataset,
        rubric_path=args.rubric
    ))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

