"""
VERITAS AI — Regression Suite & CI Gatekeeper Service
"""
import uuid
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.models.regression import RegressionRun, RegressionCaseResult, GatePolicy
from backend.app.models.prompt import PromptVersion
from backend.app.models.dataset import DatasetVersion, DatasetCase
from backend.app.models.evaluator import EvaluatorVersion, Rubric
from backend.app.providers.base import BaseLLMProvider
from backend.app.evaluators.judge import evaluate_with_judge
from backend.app.evaluators.rubric import DEFAULT_CREDIT_MEMO_RUBRIC
from backend.app.statistics.wilcoxon import compute_paired_comparison
from backend.app.services.audit_service import record_audit_event


async def execute_regression_run(
    db: Session,
    project_id: uuid.UUID,
    baseline_prompt_version_id: uuid.UUID,
    candidate_prompt_version_id: uuid.UUID,
    dataset_version_id: uuid.UUID,
    evaluator_version_id: uuid.UUID,
    provider: BaseLLMProvider,
    trigger: str = "github_pr",
    ci_run_url: Optional[str] = None,
    actor_email: str = "system@veritas.ai"
) -> RegressionRun:
    """
    Executes full regression evaluation comparing baseline and candidate prompts.
    """
    baseline_pv = db.query(PromptVersion).filter(PromptVersion.id == baseline_prompt_version_id).first()
    candidate_pv = db.query(PromptVersion).filter(PromptVersion.id == candidate_prompt_version_id).first()
    dataset_v = db.query(DatasetVersion).filter(DatasetVersion.id == dataset_version_id).first()
    eval_v = db.query(EvaluatorVersion).filter(EvaluatorVersion.id == evaluator_version_id).first()

    if not baseline_pv or not candidate_pv or not dataset_v:
        raise ValueError("Invalid prompt or dataset versions specified for regression run.")

    # Check evaluator calibration gate
    if eval_v and eval_v.calibration_status == "FAILED":
        reg_run = RegressionRun(
            id=uuid.uuid4(),
            project_id=project_id,
            trigger=trigger,
            baseline_prompt_version_id=baseline_prompt_version_id,
            candidate_prompt_version_id=candidate_prompt_version_id,
            dataset_version_id=dataset_version_id,
            evaluator_version_id=evaluator_version_id,
            status="FAILED",
            gate_decision="BLOCK",
            decision_reason="Evaluator failed calibration standards. Gating locked.",
            ci_run_url=ci_run_url
        )
        db.add(reg_run)
        db.commit()
        return reg_run

    reg_run = RegressionRun(
        id=uuid.uuid4(),
        project_id=project_id,
        trigger=trigger,
        baseline_prompt_version_id=baseline_prompt_version_id,
        candidate_prompt_version_id=candidate_prompt_version_id,
        dataset_version_id=dataset_version_id,
        evaluator_version_id=evaluator_version_id,
        status="RUNNING",
        gate_decision="PENDING",
        ci_run_url=ci_run_url
    )
    db.add(reg_run)
    db.commit()

    cases = db.query(DatasetCase).filter(DatasetCase.dataset_version_id == dataset_version_id).all()
    rubric = DEFAULT_CREDIT_MEMO_RUBRIC

    baseline_scores: List[float] = []
    candidate_scores: List[float] = []
    blocking_newly_failing = 0
    major_newly_failing = 0

    for case in cases:
        # 1. Generate Baseline Output
        base_gen = await provider.generate(
            prompt=f"{baseline_pv.prompt_template}\n\nPayload:\n{case.input_payload}",
            system_instruction=baseline_pv.system_instruction
        )
        base_evals = await evaluate_with_judge(
            provider=provider,
            rubric=rubric,
            source_payload=case.input_payload,
            candidate_output=base_gen.text,
            expected_criteria=case.expected_criteria
        )
        # Primary score: factual accuracy or composite
        base_fa = next((e["score"] for e in base_evals if e["dimension"] == "factual_accuracy"), 1.0)
        baseline_scores.append(float(base_fa))

        # 2. Generate Candidate Output
        cand_gen = await provider.generate(
            prompt=f"{candidate_pv.prompt_template}\n\nPayload:\n{case.input_payload}",
            system_instruction=candidate_pv.system_instruction
        )
        cand_evals = await evaluate_with_judge(
            provider=provider,
            rubric=rubric,
            source_payload=case.input_payload,
            candidate_output=cand_gen.text,
            expected_criteria=case.expected_criteria
        )
        cand_fa = next((e["score"] for e in cand_evals if e["dimension"] == "factual_accuracy"), 1.0)
        candidate_scores.append(float(cand_fa))

        # Determine verdict
        delta = cand_fa - base_fa
        was_pass = base_fa >= 0.7
        now_pass = cand_fa >= 0.7

        if was_pass and not now_pass:
            verdict = "newly_failing"
            if case.severity == "blocking":
                blocking_newly_failing += 1
            elif case.severity == "major":
                major_newly_failing += 1
        elif not was_pass and now_pass:
            verdict = "newly_passing"
        elif abs(delta) < 0.02:
            verdict = "unchanged"
        else:
            verdict = "improved" if delta > 0 else "regressed"

        case_res = RegressionCaseResult(
            id=uuid.uuid4(),
            regression_run_id=reg_run.id,
            dataset_case_id=case.id,
            baseline_score=base_fa,
            candidate_score=cand_fa,
            delta=delta,
            case_verdict=verdict
        )
        db.add(case_res)

    # 3. Statistical Analysis
    stats_res = compute_paired_comparison(baseline_scores, candidate_scores)

    # 4. Gate Policy Decision
    gate_policy = db.query(GatePolicy).filter(GatePolicy.project_id == project_id, GatePolicy.is_default == True).first()
    max_major = gate_policy.max_major_failures if gate_policy else 2
    allow_blocking = gate_policy.allow_blocking_failures if gate_policy else 0

    if blocking_newly_failing > allow_blocking:
        gate_decision = "BLOCK"
        decision_reason = f"{blocking_newly_failing} blocking-severity test case(s) newly failed."
    elif major_newly_failing > max_major:
        gate_decision = "BLOCK"
        decision_reason = f"{major_newly_failing} major-severity test cases newly failed (exceeded threshold of {max_major})."
    elif stats_res["significant_regression"]:
        gate_decision = "ALLOW_WITH_WARNING"
        decision_reason = f"Statistically significant net quality drop (Wilcoxon p={stats_res['p_value']}, Cliff's Delta={stats_res['effect_size']})."
    else:
        gate_decision = "ALLOW"
        decision_reason = "All critical institutional caskets and statistical parity gates satisfied."

    reg_run.status = "COMPLETED"
    reg_run.gate_decision = gate_decision
    reg_run.decision_reason = decision_reason
    reg_run.wilcoxon_p_value = stats_res["p_value"]
    reg_run.effect_size = stats_res["effect_size"]
    reg_run.summary_stats = stats_res
    reg_run.completed_at = datetime.datetime.now(datetime.timezone.utc)

    db.commit()
    db.refresh(reg_run)

    record_audit_event(
        db=db,
        project_id=project_id,
        actor_email=actor_email,
        event_type="REGRESSION_GATE_EXECUTED",
        payload={
            "regression_run_id": str(reg_run.id),
            "gate_decision": gate_decision,
            "decision_reason": decision_reason,
            "blocking_failures": blocking_newly_failing,
            "major_failures": major_newly_failing,
            "wilcoxon_p_value": stats_res["p_value"],
            "effect_size": stats_res["effect_size"]
        }
    )

    return reg_run

