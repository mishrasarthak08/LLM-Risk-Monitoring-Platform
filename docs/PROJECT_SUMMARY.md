# LLM Model-Risk Monitoring Platform: Project Summary

This document serves as a comprehensive overview of the LLM Model-Risk Monitoring Platform built over the course of the project. It details the architecture, the specific features implemented, and how the components interlock to provide a robust, SR 11-7 compliant governance system for generative AI applications.

---

## 1. Core Architecture & Evidence Schema (Phase 1 & 2)
To satisfy strict audit and compliance requirements, the foundation of the platform is an **append-only PostgreSQL evidence database**.
- **SQLAlchemy & Alembic**: Used to define and migrate the database schema securely.
- **Async Tracing Client**: A Python decorator (`@traced_call`) that development teams can wrap around their LLM calls. It asynchronously captures inputs, outputs, timestamps, and model configurations, routing them into a `run_traces` table without adding latency to the main application thread.
- **Immutability**: The schema is designed such that historical traces, judge scores, and drift events cannot be altered, ensuring a cryptographically sound audit trail.

## 2. Immutable Golden Sets (Phase 3)
A systematic approach to defining the "ground truth" against which LLM changes are evaluated.
- **JSONL-based Storage**: Test cases are stored in structured JSONL files, representing diverse edge cases and expected behaviors.
- **Diff Utility**: A custom script (`ci/golden_set_diff.py`) that computes the delta between two versions of a Golden Set, categorizing changes into added, removed, and modified cases to ensure reviewers understand how the benchmark is evolving.

## 3. LLM-as-a-Judge Calibration Engine (Phase 4)
Because manual human review of thousands of LLM outputs is unscalable, we built an automated scoring engine that is rigorously mathematically validated.
- **Rubric Engine**: YAML-based rubrics that define the dimensions of quality (e.g., factual accuracy, tone, refusal rate) and how the LLM Judge should evaluate them.
- **Human Agreement Calibration**: A statistical calibration script (`monitoring/judge/calibration/agreement.py`) that computes **Cohen's Kappa** between the LLM Judge and human reviewers. The Judge is only marked as "calibrated" and allowed to be used in CI if it meets strict agreement thresholds.

## 4. Automated Regression Suite & CI Gating (Phase 5)
An intelligent gatekeeper built natively into the CI process to prevent degraded prompts from reaching production.
- **Regression Runner**: Executes candidate prompts against the Golden Set and compares the scores to the baseline.
- **Statistical Comparator**: Uses the **Wilcoxon signed-rank test** to detect subtle, aggregate degradation across the dataset, rather than just looking at binary pass/fail rates.
- **GitHub Actions Integration**: A workflow (`.github/workflows/on_prompt_change.yml`) that automatically runs the suite whenever prompt files or model configs are modified, blocking the PR and posting a detailed Markdown report if degradation is detected.

## 5. Continuous Production Drift Detection (Phase 6)
Monitoring live production traffic for distributional shifts, independent of prompt changes (e.g., detecting if user behavior changes or the underlying foundation model silently updates).
- **Population Stability Index (PSI)**: Monitors shifts in the distribution of Judge scores (e.g., a sudden drop in Factual Accuracy).
- **Kolmogorov-Smirnov (KS) Test**: Detects structural shifts in output token lengths.
- **Two-Proportion Z-Test**: Identifies statistically significant spikes in LLM refusal rates.
- **Scheduler**: A cron-ready job (`monitoring/drift/scheduler_job.py`) that periodically fetches a rolling window of production traces and compares them to a pinned baseline distribution.

## 6. Failure Analysis Workbench (Phase 7)
A set of interactive **Streamlit** dashboards designed for engineers and risk officers to triage issues visually.
- **CI Failure View**: Allows engineers to drill down into exactly which cases failed during a blocked PR, viewing the baseline vs. candidate outputs side-by-side.
- **Production Drift View**: Visualizes the statistical drift metrics over time, helping on-call engineers determine if an alert is a genuine quality incident or a benign population shift.

## 7. Compliance Packaging & Operations (Phase 8)
Translating the technical system into enterprise-ready operational processes.
- **Operational Runbooks**: Detailed playbooks for on-call engineers handling CI gate overrides (`regression_blocked.md`), production drift alerts (`critical_drift_alert.md`), and stale judges (`judge_recalibration.md`).
- **Regulatory Mapping**: A formal compliance document (`docs/compliance/SR11_7_Mapping.md`) that explicitly maps the system's technical capabilities to the Federal Reserve's SR 11-7 expectations for Model Risk Management.

---

## Next Steps & Handoff

The platform is now structurally complete, fully typed, linted, and covered by a suite of passing unit tests. 

To proceed with deploying this to a real environment, the next steps would involve:
1. Provisioning the actual PostgreSQL database and configuring the Alembic connection strings.
2. Replacing the mocked `mock_llm_call` implementations with live API calls to your provider (e.g., Gemini, OpenAI).
3. Deploying the Streamlit application to an internal hosting provider.
4. Hooking the GitHub Actions workflow into your live repository.
