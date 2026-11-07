# VERITAS AI — Comprehensive Architecture Audit & Repository Assessment

**Document ID:** AUDIT-2026-001  
**Target Platform:** VERITAS AI (Enterprise LLM Reliability, Evaluation, Observability, and Governance Platform)  
**Auditor:** Principal Software Architect & Systems Evaluation Team  
**Date:** November 2026  
**Status:** Completed  

---

## 1. Executive Summary

This audit evaluates the pre-existing codebase (`LLM-Risk-Monitoring-Platform-1`) against the requirements of an elite, enterprise-grade AI governance and observability platform (**VERITAS AI**). The existing codebase contains valuable initial prototypes of statistical tests (Wilcoxon, Cohen's Kappa, PSI, KS test) and a schema framework, but suffers from severe structural limitations:

1. **Absence of an Application API Layer:** The existing architecture has no REST/OpenAPI backend. The Streamlit dashboard queries PostgreSQL directly via raw SQLAlchemy sessions, creating tight coupling, lack of authorization boundaries, and zero headless integration capabilities.
2. **Single-Tenant Hardcoding:** All tables, traces, and metrics assume a single global tenant and hardcoded feature (`credit_memo_v1`). There are no concepts of Organizations, Projects, Users, API Keys, or Role-Based Access Control (RBAC).
3. **Data Loss & Observability Gaps:** The tracing decorator relies on an in-memory queue with an aggressive drop-oldest policy that silently discards critical audit records during load spikes or database unavailability. There is no durable buffering, dead-letter storage, or context propagation across microservices.
4. **Statistical Naivety:** Statistical gates rely solely on p-values without accounting for statistical power, minimum sample size requirements, effect size estimation, or multiple comparison corrections.
5. **No Verification Mechanism for Audit Logs:** Although tables are called "append-only," there is no cryptographic tamper-evident verification (such as a cryptographic hash-chain or Merkle tree) to mathematically prove historical records have not been altered.
6. **Frontend Limitations:** The Streamlit prototype has several hardcoded mock UI fallbacks, static visualization charts, and lacks modern enterprise workflows (e.g. interactive syntax-highlighted prompt versioning, dataset uploading, interactive annotation/adjudication, span hierarchy waterfall views).

---

## 2. Component-by-Component Audit

### 2.1 Backend & APIs
- **Existing State:** Non-existent. No FastAPI or Flask service exists. Scripts are executed directly from CLI or invoked within Streamlit rendering loops.
- **Evaluation:** **Critical Flaw.** An enterprise developer platform requires a clean, high-performance, asynchronous REST API with OpenAPI documentation, standard HTTP status codes, structured error envelopes, and request ID tracking.
- **Action:** Build a production-grade FastAPI backend with Pydantic v2 schemas, dependency injection for auth/DB sessions, rate limiting, and modular domain routers.

### 2.2 Database Architecture & Multi-Tenancy
- **Existing State:** PostgreSQL schema defined in `monitoring/db/models.py` with 11 tables (`run_traces`, `prompt_versions`, `model_configs`, `golden_set_versions`, `golden_set_cases`, `judge_versions`, `judge_scores`, `regression_runs`, `regression_case_results`, `drift_reference_distributions`, `drift_events`).
- **Deficiencies:**
  - No `organizations`, `users`, `memberships`, `projects`, or `api_keys` tables.
  - Foreign keys lack tenant partitioning, creating data contamination risks across projects.
  - No cryptographic chaining (`previous_record_hash`) on immutable audit tables.
  - Missing operational tables for notification channels, webhook deliveries, and human annotation workflows.
- **Action:** Re-engineer the schema in SQLAlchemy 2.0 to introduce full multi-tenancy, cryptographic audit chains, evaluation runs, and annotation datasets, managed cleanly via Alembic.

### 2.3 Observability & Tracing Engine (`monitoring/tracing/`)
- **Existing State:** A Python decorator `@traced_call` in `decorators.py` backed by `async_writer.py` using `queue.Queue(maxsize=1000)` and a single background thread.
- **Deficiencies:**
  - `enqueue_trace()` silently drops the oldest trace when the queue is full (`trace_queue.get_nowait()`). In regulated finance, silently dropping audit traces violates SR 11-7.
  - DB calls to resolve `prompt_version_id` and `model_config_id` occur synchronously inside the execution wrapper before invoking the LLM, introducing database latency into the critical user path.
  - No data redaction (PII/sensitive financial terms are written raw).
  - No sampling controls.
- **Action:** Implement a dual-mode tracing engine: a high-throughput, non-blocking ingestion endpoint in FastAPI supporting batch spans, context propagation (Trace ID / Span ID hierarchy), automatic PII/covenant redaction, configurable sampling, and durable fallback storage.

### 2.4 Model Provider Abstraction & Client Layer (`app/client.py`)
- **Existing State:** Single hardcoded client in `app/client.py` importing Google Gemini SDK (`genai.Client`) with an in-memory dictionary cache.
- **Deficiencies:**
  - No interface or provider abstraction layer. Adding Anthropic, OpenAI, or a local model requires refactoring core feature code.
  - No simulated / mock provider for unit testing or CI runs, making tests fail or stall when external API quota/keys are unavailable.
- **Action:** Build an extensible `ProviderAdapter` ABC with concrete implementations:
  - `GeminiProviderAdapter` (using official `google-genai` SDK with backoff retries).
  - `OpenAIProviderAdapter` & `AnthropicProviderAdapter` interfaces.
  - `SimulatedProviderAdapter` (deterministic, zero-cost, high-fidelity mock generator for automated CI test suites and offline demo narratives).

### 2.5 Evaluation Engine & LLM-as-a-Judge (`monitoring/judge/`)
- **Existing State:** `scorer.py` evaluates single candidate outputs by string-formatting prompts with source data and expecting JSON. Includes basic regex keyword checks in `checks.py`.
- **Deficiencies:**
  - Prompts parse JSON with crude string stripping (`startswith("```json")`), which is fragile.
  - The judge is treated as an oracle; failure modes and model uncertainty are not surfaced.
  - No support for human evaluations, custom metric plugins, or multi-judge consensus.
- **Action:** Build a modular `EvaluationEngine` supporting:
  - Validated Pydantic structured output parsing with repair mechanisms.
  - Deterministic evaluation assertions (exact match, numerical tolerances, regex, forbidden term checks).
  - Multi-dimensional LLM-as-a-Judge rubrics with evidence citation.
  - Human evaluation and annotation scoring pipelines.

### 2.6 Golden Dataset Management (`monitoring/golden_set/`)
- **Existing State:** JSONL files loaded via `loader.py` and validated by Pydantic `schema.py`.
- **Deficiencies:**
  - Files live solely in the Git filesystem; cannot be created, uploaded, versioned, or tagged through an API or UI.
  - Dataset hashes are simple string hashes without version comparison metadata or approval governance.
- **Action:** Build a database-backed, content-addressed Dataset Registry supporting JSONL import/export, dataset schema validation, category tagging, severity assignment, and version immutability.

### 2.7 Regression Testing & Statistical Gating (`monitoring/regression/`)
- **Existing State:** `runner.py` and `comparator.py` execute candidate vs. baseline prompts, compute Wilcoxon signed-rank test p-values, and check if blocking cases failed.
- **Deficiencies:**
  - Relies solely on p-value ($p < 0.05$). Wilcoxon with small sample sizes ($N < 10$) has virtually zero statistical power to detect real degradation, while with large $N$, minute non-material differences yield $p < 0.001$.
  - Does not compute effect sizes (e.g., Rank-Biserial Correlation or Cliff's Delta).
  - Does not verify minimum sample size requirements before drawing statistical conclusions.
- **Action:** Rebuild the `RegressionComparator` to calculate:
  - Paired Wilcoxon signed-rank test with continuity correction.
  - Effect size (Rank-Biserial correlation $r$ and Cliff's Delta).
  - Exact counts of `improved`, `unchanged`, `regressed`, `newly_failing`, and `newly_passing`.
  - Configurable multi-rule gate policy engine (blocking severity thresholds, maximum allowed major regressions, effect-size degradation limits).

### 2.8 Continuous Drift Monitoring (`monitoring/drift/`)
- **Existing State:** `detectors.py` implements PSI, KS-test, and 2-proportion Z-test. `scheduler_job.py` polls 24h rolling traces.
- **Deficiencies:**
  - PSI calculation does not handle degenerate edge cases cleanly (e.g., zero-variance predictions, identical quantiles).
  - No check on minimum required sample sizes (running KS on $N=5$ produces meaningless p-values).
  - No multiple-comparison adjustments (Bonferroni/FDR) when evaluating multiple metrics simultaneously.
  - Triage states are primitive and lack structured root-cause tracking or resolution history.
- **Action:** Implement a robust `StatisticalDriftEngine` with minimum sample thresholds ($N \ge 30$), quantile smoothing, effect size tracking, and a full incident management lifecycle (`OPEN` -> `INVESTIGATING` -> `CONFIRMED_ISSUE` / `BENIGN_SHIFT` / `FALSE_POSITIVE` -> `RESOLVED`).

### 2.9 Judge Calibration Engine (`monitoring/judge/calibration/`)
- **Existing State:** Computes Cohen's Kappa between human and judge lists.
- **Deficiencies:**
  - Requires single flat arrays; does not support multiple human raters, disagreement resolution, or confusion matrices.
  - Does not compute standard error or confidence intervals for Kappa.
- **Action:** Build an enterprise `CalibrationService` computing:
  - Unweighted Cohen's Kappa for binary criteria.
  - Linear/Quadratic Weighted Kappa for ordinal criteria.
  - Confusion matrices, precision, recall, and specific rater agreement metrics.
  - Enforced gate rule: Uncalibrated judges are strictly barred from gating production deployments.

### 2.10 Audit, Governance & Regulatory Reporting (`docs/compliance/`)
- **Existing State:** Markdown document mapping SR 11-7 to theoretical platform files. Streamlit report generator creates dummy downloads.
- **Deficiencies:**
  - No cryptographically verifiable audit trail.
  - No real PDF/JSON/CSV export generation.
- **Action:** Implement cryptographic SHA-256 hash-chaining on all audit events (`audit_events` with `previous_hash` and `record_hash`). Provide a CLI/API integrity verification tool. Build a real multi-format export generator (JSON, CSV, PDF) packaging comprehensive SR 11-7 evidence.

### 2.11 Frontend User Experience
- **Existing State:** Streamlit app.
- **Deficiencies:**
  - Not an enterprise SaaS experience.
  - Lacks granular UI components, interactive prompt diffing, span hierarchy trees, or responsive data grids.
  - Cannot be embedded or integrated with enterprise authentication providers.
- **Action:** Build a modern, responsive, high-performance web application in Next.js (App Router), React, TypeScript, Tailwind CSS, shadcn/ui design language, and TanStack Query.

---

## 3. Disposition Matrix

| Component | Status | Action | Rationale |
| :--- | :--- | :--- | :--- |
| **Statistical Foundations** (PSI, Wilcoxon, KS, Kappa) | Preserved & Upgraded | Refactor into `veritas_ai.statistics` | Core mathematics are sound but require sample-size guards, effect sizes, and edge-case handling. |
| **Golden Set Benchmark Data** (`v0001_credit_memo.jsonl`) | Preserved & Expanded | Port to database seeding | High-quality domain credit memo scenarios (DSCR, prompt injection, divide-by-zero). |
| **Rubric Dimensions** (`credit_memo_rubric_v2.yaml`) | Preserved & Expanded | Port to DB Rubric Registry | Clear, defensible banking evaluation dimensions. |
| **Streamlit Dashboard** | Replaced | Replace with Next.js + React + Tailwind + shadcn/ui | Streamlit cannot deliver the required enterprise-grade UX, strict TypeScript client, or integration capabilities. |
| **Direct DB Script Execution** | Replaced | Replace with FastAPI REST API | Required for headless CI integration, secure authorization, and separation of concerns. |
| **In-Memory Unbuffered Tracing** | Replaced | Replace with Structured FastAPI Ingestion & Context Engine | Eliminates silent trace drops and unblocks user-facing request latency. |
| **Single-Tenant Database Schema** | Replaced | Rebuild with SQLAlchemy 2.0 multi-tenant schema | Necessary for enterprise organizations, projects, API keys, and audit integrity. |

---

## 4. Architectural Target Summary

The re-engineered **VERITAS AI** architecture will be structured as a clean, modular monolith:
- **`backend/`**: FastAPI application with clean hexagonal layers (`api/`, `services/`, `models/`, `evaluators/`, `statistics/`, `providers/`).
- **`frontend/`**: Next.js 14+ (App Router) with TypeScript, Tailwind CSS, shadcn/ui components, and interactive Recharts visualizations.
- **`shared/`**: Versioned benchmark datasets, evaluation rubrics, and configurations.
- **`tests/`**: Pytest test suite covering unit tests, API integration tests, statistical correctness, tamper-evident audit logs, and provider simulators.
- **`docs/`**: Complete architecture specifications, API documentation, runbooks, and compliance mapping.

