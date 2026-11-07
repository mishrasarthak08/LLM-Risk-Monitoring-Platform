# VERITAS AI — Implementation Roadmap & Execution Plan

**Document ID:** ROADMAP-2026-001  
**Project:** VERITAS AI Platform Rebuild  
**Status:** Approved for Implementation  

---

## 1. Roadmap Overview & Phasing

The rebuild executes across 9 disciplined stages, progressing from foundational data models and services to complete end-to-end integration, frontend interface, and test verification.

```
Stage 1: Repository Audit & Architecture Definition (Done)
   │
   ▼
Stage 2: Core Engineering Foundations (FastAPI, SQLAlchemy 2.0, Multi-Tenant Schema, Auth)
   │
   ▼
Stage 3: Core Vertical Slice (Traces, Spans, Ingestion, Context Propagation, Gemini & Simulator)
   │
   ▼
Stage 4: Evaluation & Golden Dataset Infrastructure (Rubrics, Deterministic + LLM Judges, Datasets)
   │
   ▼
Stage 5: Regression Testing & CI Gatekeeper (Wilcoxon Test, Effect Sizes, Gate Policy, CI CLI)
   │
   ▼
Stage 6: Statistical Drift Detection & Incident Desk (PSI, KS Test, Z-Test, Triage Workflow, Slack)
   │
   ▼
Stage 7: Judge Calibration & Human Annotation (Cohen's Kappa, Confusion Matrices, Adjudication)
   │
   ▼
Stage 8: Cryptographic Audit Trail & Governance Evidence (Hash-Chain, Verifier CLI, SR 11-7 Exports)
   │
   ▼
Stage 9: Enterprise Next.js Frontend & End-to-End Verification (App Router, Recharts, Polish, Tests)
```

---

## 2. Detailed Stage Breakdown

### Stage 1: Repository Audit & Architecture Definition
- [x] Complete comprehensive codebase inspection.
- [x] Create `docs/ARCHITECTURE_AUDIT.md`.
- [x] Create `docs/IMPLEMENTATION_ROADMAP.md`.
- [x] Create `docs/ARCHITECTURE.md`.

### Stage 2: Core Engineering Foundations
- [x] Directory restructuring: `backend/`, `frontend/`, `docs/`, `scripts/`, `config/`.
- [x] Virtual environment and dependency management via `pyproject.toml` and `uv` / `pip`.
- [x] Database architecture: Multi-tenant SQLAlchemy 2.0 models:
  - `organizations`, `users`, `memberships`, `projects`, `api_keys`.
  - `prompts`, `prompt_versions`, `model_configs`.
  - `datasets`, `dataset_versions`, `dataset_cases`.
  - `traces`, `spans`, `evaluators`, `evaluator_versions`, `evaluation_runs`, `evaluation_results`.
  - `human_annotations`, `calibration_runs`, `regression_runs`, `regression_case_results`.
  - `drift_reference_distributions`, `drift_events`, `audit_events`.
- [x] Database migration management with Alembic.
- [x] Security layer: API key verification, native bcrypt hashing, JWT bearer authentication, role-based access control (Admin, Member, Viewer).
- [x] FastAPI foundation: structured exceptions, standard JSON envelopes, CORS, request correlation IDs.

### Stage 3: Core Vertical Slice (Tracing & Provider Abstraction)
- [x] Provider Abstraction Layer:
  - `BaseLLMProvider` interface.
  - `SimulatedProvider`: High-fidelity, deterministic generator for offline testing and demo consistency.
  - `GeminiProvider`: Real Google Gemini API adapter (`gemini-2.5-flash`) with exponential retry backoff.
- [x] Tracing Engine:
  - Traces and hierarchical Spans (`parent_span_id`).
  - Python context manager and decorator (`@veritas_trace`).
  - Sensitive data redactor (SSNs, account numbers, card numbers, covenant details).
  - High-throughput asynchronous ingestion endpoint (`POST /api/v1/traces/ingest`).
  - Token and financial cost computation against model pricing tables.

### Stage 4: Evaluation & Golden Dataset Infrastructure
- [x] Golden Dataset Registry:
  - Dataset versioning with SHA-256 content hashing.
  - JSONL import/export with Pydantic validation.
  - Pre-seeded realistic synthetic commercial banking test cases.
- [x] Multi-Dimensional Evaluation Engine:
  - Rubric definitions (YAML and DB backed).
  - Deterministic evaluators: exact string match, regex patterns, numerical tolerance, required covenants, forbidden terms.
  - LLM-as-a-Judge: isolated dimensional scoring, structured JSON parsing with repair fallback, reasoning, and citation evidence.
  - Evaluation run coordinator.

### Stage 5: Regression Engine & CI Gatekeeper
- [x] Paired comparison algorithm (`baseline` vs. `candidate`).
- [x] Statistical engine:
  - Paired Wilcoxon signed-rank test.
  - Sample size sufficiency checks ($N \ge 10$ for Wilcoxon).
  - Effect size estimation (Rank-Biserial Correlation & Cliff's Delta).
- [x] Gate Policy Engine:
  - Configurable rules: blocking severity zero-tolerance, major severity threshold, statistically significant deterioration warnings.
- [x] Headless CI CLI command (`ci/veritas_ci.py`) suitable for GitHub Actions.
- [x] PR Markdown report generator with detailed failure breakdowns.

### Stage 6: Continuous Drift Monitoring & Incident Management
- [x] Statistical Drift Engine:
  - Population Stability Index (PSI) with robust quantile binning and zero-division handling.
  - Two-sample Kolmogorov-Smirnov test for continuous output distributions.
  - Two-proportion Z-test for failure/refusal rate anomalies.
  - Minimum sample size enforcement ($N \ge 30$).
- [x] Scheduled execution service & Celery/cron integration.
- [x] Drift Incident Desk:
  - Incident states: `OPEN`, `INVESTIGATING`, `CONFIRMED_ISSUE`, `BENIGN_SHIFT`, `FALSE_POSITIVE`, `RESOLVED`.
  - Human triage notes, root-cause categorization, and resolution persistence.
  - Webhook dispatcher (Slack notification payloads).

### Stage 7: Evaluator Calibration Engine
- [x] Calibration Framework:
  - Unweighted Cohen's Kappa for binary criteria.
  - Linear/Quadratic Weighted Cohen's Kappa for ordinal criteria.
  - Confusion matrix generation, precision, recall, and observed vs. expected agreement.
  - Per-dimension pass/fail status.
- [x] Calibration Gate Rule:
  - Evaluators with $\kappa < \text{threshold}$ are locked from acting as automated CI deployment gates.
- [x] Human annotation & adjudication workbench API.

### Stage 8: Cryptographic Audit Trail & Governance Evidence
- [x] Tamper-Evident Audit Ledger:
  - `audit_events` table with cryptographic SHA-256 hash chaining:
    $$\text{hash}_n = \text{SHA256}(\text{hash}_{n-1} + \text{payload}_n + \text{timestamp}_n)$$
  - Cryptographic verification utility (`ci/veritas_audit.py`) checking ledger chain integrity.
- [x] Regulatory Compliance Package Generator:
  - Comprehensive evidence builder mapping directly to SR 11-7 / OCC 2011-12 controls.
  - Multi-format exports: structured JSON, flattened CSV, and styled PDF/HTML reports.

### Stage 9: Enterprise Next.js Frontend & System Verification
- [x] Next.js 14+ App Router frontend with TypeScript and Tailwind CSS.
- [x] Component architecture with modern design language and Lucide icons.
- [x] Core pages:
  - Overview / Executive Dashboard (`/`).
  - Traces & Span Hierarchy Inspector (`/traces`).
  - Prompts & Version History Registry (`/prompts`).
  - Benchmark Datasets Management (`/datasets`).
  - Regression Testing & Failure Analysis (`/regressions`).
  - Drift Monitoring & Incident Desk (`/drift`).
  - Evaluator Calibration & Agreement (`/calibration`).
  - Cryptographic Audit & Compliance Ledger (`/audit`).
  - Governance Dossier & Compliance Exporter (`/reports`).
- [x] Automated test suite verification: Pytest covering unit, API integration, statistical correctness, and cryptographic verification.
- [x] Documentation, local startup instructions, Makefile, and Docker Compose configuration.

