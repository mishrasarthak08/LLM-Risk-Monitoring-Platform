# VERITAS AI — Target System Architecture & Design Specification

**Platform Name:** VERITAS AI  
**Scope:** Enterprise LLM Reliability, Evaluation, Observability, and Governance Platform  
**Standard Compliance:** Federal Reserve SR 11-7 / OCC 2011-12 Model Risk Management  
**Version:** 2.0.0  
**Status:** Living Specification  

---

## 1. Architectural Philosophy & Principles

VERITAS AI is engineered under four foundational tenets:

1. **Defense-Grade Evidentiary Integrity:**
   Every output, score, prompt, and configuration must trace back to a mathematically verifiable provenance. Historical records are immutable; critical audit events are chained via SHA-256 cryptographic hashes.
2. **Decoupled, Zero-Interference Observability:**
   Tracing LLM applications must never degrade user-facing performance or introduce single points of failure. Ingestion paths must be asynchronous, idempotent, buffered, and resilient against database outages.
3. **Rigorous, Honest Statistics:**
   Statistical decisions must not hide behind naive p-values. Gating and drift engines must explicitly measure sample size sufficiency, statistical power, effect sizes (Cliff's Delta, Rank-Biserial correlation), and multiple-testing corrections.
4. **Domain Independence with Realistic Reference Implementation:**
   The core platform abstractions (Projects, Prompts, Traces, Evaluators, Rubrics, Datasets, Regressions, Drift) are 100% domain-agnostic. Commercial banking credit memo underwriting is integrated as a rich, realistic reference application.

---

## 2. High-Level Architecture Diagram

```
                                 ┌────────────────────────────────────────┐
                                 │       Next.js 14 Web Frontend          │
                                 │ (TypeScript, Tailwind, shadcn, Recharts)│
                                 └───────────────────▲────────────────────┘
                                                     │ HTTPS / REST / JSON
                                                     ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                VERITAS AI FastAPI Backend                              │
│                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │                    API Layer (FastAPI Routers, Auth, RBAC)                       │  │
│  │  /traces  /prompts  /datasets  /evaluations  /regressions  /drift  /calibration  │  │
│  └──────────────────────────────────────▲───────────────────────────────────────────┘  │
│                                         │                                              │
│  ┌──────────────────────────────────────┴───────────────────────────────────────────┐  │
│  │                              Core Service Domains                                │  │
│  │  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐  ┌─────────────┐  │  │
│  │  │ Observability   │  │ Evaluation       │  │ Regression     │  │ Drift       │  │  │
│  │  │ & Tracing       │  │ Engine & Rubrics │  │ CI Gatekeeper  │  │ Monitor     │  │  │
│  │  └─────────────────┘  └──────────────────┘  └────────────────┘  └─────────────┘  │  │
│  │  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐  ┌─────────────┐  │  │
│  │  │ Dataset         │  │ Judge            │  │ Cryptographic  │  │ Governance  │  │  │
│  │  │ Versioning      │  │ Calibration      │  │ Audit Ledger   │  │ Exporter    │  │  │
│  │  └─────────────────┘  └──────────────────┘  └────────────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────┬───────────────────────────────────────────┘  │
│                                         │                                              │
│  ┌──────────────────────────────────────┴───────────────────────────────────────────┐  │
│  │                       Data & External Adapter Subsystem                          │  │
│  │  ┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────┐  │  │
│  │  │ SQLAlchemy 2.0 ORM      │ │ Provider Adapters       │ │ Statistical Engine  │  │  │
│  │  │ (PostgreSQL Repository) │ │ (Gemini, Sim, OpenAI)   │ │ (SciPy, Statsmodels)│  │  │
│  └──┴────────────▲────────────┴─┴────────────▲────────────┴─┴──────────▲──────────┴──┘  │
└──────────────────┼───────────────────────────┼─────────────────────────┼────────────────┘
                   │                           │                         │
                   ▼                           ▼                         ▼
          ┌───────────────────┐     ┌─────────────────────┐     ┌─────────────────┐
          │    PostgreSQL     │     │ External LLM APIs   │     │ Redis / Queue   │
          │ Relational Store  │     │ (Google Gemini API) │     │ Background Jobs │
          └───────────────────┘     └─────────────────────┘     └─────────────────┘
```

---

## 3. Core Subsystem Specifications

### 3.1 Multi-Tenant Data & Security Architecture
All entities belong to an `organization_id` and `project_id`. Authentication supports:
- **Session Tokens / Bearer JWTs:** For browser users interacting with the frontend.
- **Scoped API Keys (`vai_live_...`):** For SDKs, CI/CD pipelines, and microservices.
- **RBAC Roles:** `OWNER`, `ADMIN`, `MEMBER`, `VIEWER`.

### 3.2 Trace & Observability Subsystem
- **Spans & Context:** Traces contain one or more Spans forming a tree (`span_id`, `parent_span_id`).
- **Data Redaction:** Built-in pattern redactor sanitizes credit card numbers, US SSNs, banking account details, and custom sensitive tokens before persistence.
- **Token & Cost Accounting:** Granular input and output token counting computed against a versioned model pricing matrix (`config/model_pricing.yaml`).

### 3.3 Provider Abstraction Layer
- **`SimulatedProvider`:** Generates realistic, reproducible outputs based on hash-seeded responses. Used for automated integration tests, CI pipelines, and offline demonstrations without requiring live API keys.
- **`GeminiProvider`:** Connects to Google Gemini (`gemini-2.5-flash`), with exponential jittered retry, token usage extraction, and connection pooling.

### 3.4 Evaluation Subsystem
Evaluations can run deterministically or via LLM-as-a-Judge:
- **Deterministic:** Regex assertions, keyword inclusions (`must_mention`), exclusions (`must_not`), numeric threshold checks (e.g., DSCR $\ge 1.25$).
- **LLM-as-a-Judge:** Structured Pydantic output schemas requiring both quantitative scores and qualitative textual rationale citing evidence from source inputs.
- **Rubrics:** Version-controlled multi-dimensional rubrics (`factual_accuracy`, `policy_compliance`, `completeness`, `reasoning_quality`, `tone_clarity`).

### 3.5 Regression Testing Engine
- Runs candidate vs. baseline prompts across identical dataset versions.
- Calculates paired score deltas and Wilcoxon signed-rank test p-values.
- Measures effect size using Rank-Biserial correlation ($r$) and Cliff's Delta.
- Enforces strict gatekeeper rules:
  - Any newly failing `blocking` case blocks the deployment.
  - $\ge 3$ newly failing `major` cases block the deployment.
  - Statistically significant net regression with moderate-to-large effect size triggers warnings or blocks according to project policy.

### 3.6 Continuous Drift Monitor
- Periodically samples production traces over a rolling window (e.g. 24h).
- Tests for:
  - **Output Length Drift:** Two-sample Kolmogorov-Smirnov test.
  - **Refusal / Error Rate Drift:** Two-proportion Z-test.
  - **Quality Score Distribution Shift:** Population Stability Index (PSI).
- Enforces minimum sample size rules ($N \ge 30$) to prevent spurious alerts on low-volume endpoints.
- Triage workflow transitions incidents through: `OPEN` $\to$ `INVESTIGATING` $\to$ `CONFIRMED_ISSUE` / `BENIGN_SHIFT` / `FALSE_POSITIVE` $\to$ `RESOLVED`.

### 3.7 Evaluator Calibration Engine
- Evaluator accuracy is calibrated against human expert annotations.
- Computes Cohen's Kappa ($\kappa$) for binary criteria and Linear/Quadratic Weighted Kappa for ordinal 1-5 scales.
- Computes full confusion matrices, sensitivity, and specificity.
- Enforces an automated safety lock: Any evaluator with $\kappa < 0.70$ on gating dimensions is blocked from participating in CI gatekeeper decisions.

### 3.8 Cryptographic Audit Ledger & Compliance
- Every governance event (prompt publication, regression decision, drift acknowledgment, baseline override) is recorded in `audit_events`.
- Each record contains:
  $$\text{record\_hash} = \text{SHA-256}(\text{previous\_hash} + \text{event\_type} + \text{payload\_json} + \text{timestamp})$$
- A standalone CLI/API verification command audits the full hash chain, providing non-repudiation and tamper detection.
- Generates comprehensive evidence packages satisfying SR 11-7 requirements in JSON, CSV, and formatted PDF formats.
