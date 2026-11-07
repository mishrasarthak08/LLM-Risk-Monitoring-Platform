# 🛡️ VERITAS AI — Enterprise LLM Reliability, Evaluation, Observability & Governance Platform

[![Build & Test](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/frontend-Next.js%2014%20App%20Router-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-336791.svg)](https://www.postgresql.org/)
[![Compliance: SR 11-7 / OCC 2011-12](https://img.shields.io/badge/compliance-SR%2011--7%20%7C%20OCC%202011--12-yellow.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**VERITAS AI** is an enterprise-grade AI reliability, evaluation, continuous observability, and governance platform designed for high-stakes generative AI applications. Engineered to satisfy rigorous model risk management requirements (**Federal Reserve SR 11-7 / OCC 2011-12**), the platform provides defense-grade mathematical validation, change-triggered CI regression gating, real-time statistical drift monitoring, and a cryptographically verifiable append-only audit trail.

---

## 🏗️ System Architecture

VERITAS AI is engineered as a modern, decoupled modular monolith:

```
                  ┌───────────────────────────────────────────────┐
                  │       Next.js 14 App Router Web Client       │
                  │  (TypeScript, Tailwind, shadcn/ui, Recharts)  │
                  └───────────────────────▲───────────────────────┘
                                          │ REST API / JSON
                                          ▼
                  ┌───────────────────────────────────────────────┐
                  │          FastAPI Application Server           │
                  │  (Pydantic v2, Async Dependency Injection)    │
                  └───────▲───────────────▲───────────────▲───────┘
                          │               │               │
         Async Telemetry  │   Evaluations │   Drift Check │
                          │               │               │
     ┌────────────────────┴──┐ ┌──────────┴──────────┐ ┌──┴─────────────────────────┐
     │  LOOP 1: PRODUCTION   │ │  LOOP 2: CI GATING  │ │  LOOP 3: CONTINUOUS DRIFT  │
     │  Zero-overhead trace  │ │  Change-triggered   │ │  24h rolling windows       │
     │  Context propagation  │ │  Wilcoxon test      │ │  KS test, Two-prop Z, PSI  │
     │  PII & secret redact  │ │  Blocking severity  │ │  Triage Incident Desk      │
     └───────────────────────┘ └─────────────────────┘ └────────────────────────────┘
                          │               │               │
                          └───────────────┼───────────────┘
                                          ▼
                  ┌───────────────────────────────────────────────┐
                  │          PostgreSQL Relational Store          │
                  │    (28 Normalized Append-Only Tables)         │
                  │   Cryptographically Chained Audit Ledger      │
                  └───────────────────────────────────────────────┘
```

---

## 🌟 The Core Capabilities

### 1. AI Observability & Trace Explorer (Module A)
- **Nested Distributed Spans:** Captures parent-child span execution trees (`parent_span_id`) across multi-step prompt chains.
- **Automated PII/Secret Redaction:** Sanitizes credit card numbers, US SSNs, banking account details, and API keys before database commitment.
- **Granular Financial Cost Accounting:** Computes exact dollar cost per call based on versioned token pricing tables.
- **Zero Silent Trace Loss:** Bounded queue with retry handling and fallback logging.

### 2. Prompt Management & Version Registry (Module B)
- **Content-Addressed Immutability:** Every version is assigned a deterministic SHA-256 content hash. Historical versions cannot be overwritten.
- **Unified Visual Diffing:** Side-by-side unified diff view comparing template changes and variable bindings across revisions.
- **Rollback by Publication:** Instantly promotes any historical release to active status.

### 3. Multi-Dimensional Evaluation Engine (Module C)
- **Deterministic Assertion Guards:** Verifies exact covenants (`must_mention`), forbidden prompt injection words (`must_not`), and numeric thresholds.
- **Isolated LLM-as-a-Judge:** Scores dimensions independently (`factual_accuracy`, `policy_compliance`, `completeness`, `reasoning_quality`, `tone_clarity`) to prevent position and verbosity bias.
- **Structured JSON Validation:** Enforces strict Pydantic parsing with automated fallback repair.

### 4. Golden Dataset Management (Module D)
- **Versioned Benchmark Collections:** Immutable test suites containing happy-path, edge-case, adversarial red-team, and known-failure scenarios.
- **Streaming JSONL Import:** Validates test case schemas, severities (`blocking`, `major`, `minor`), and ground truth criteria.

### 5. Regression Testing & CI Gatekeeper (Module E)
- **Paired Wilcoxon Signed-Rank Test:** Evaluates candidate vs. baseline distributions with continuity correction.
- **Effect Size Estimation:** Calculates Cliff's Delta and Rank-Biserial correlation $r$ alongside p-values.
- **Severity-Based Gating:** Automatically blocks pull requests if any `blocking` case newly fails or $\ge 3$ `major` cases fail.
- **Headless CI CLI:** `python ci/veritas_ci.py` returns exit code 0 (ALLOW) or 1 (BLOCK) for GitHub Actions integration.

### 6. Continuous Production Drift Detection (Module F)
- **Population Stability Index (PSI):** Quantile-based shift detection on quality scores ($< 0.10$ normal, $0.10 - 0.25$ warning, $\ge 0.25$ critical).
- **Two-Sample Kolmogorov-Smirnov Test:** Identifies continuous distribution drift in output token length and latency ($p < 0.05$).
- **Two-Proportion Z-Test:** Detects statistically significant spikes in refusal and error rates ($p < 0.05$).
- **Incident Triage Workbench:** Full lifecycle tracking (`OPEN` $\to$ `INVESTIGATING` $\to$ `CONFIRMED_ISSUE` / `BENIGN_SHIFT` / `FALSE_POSITIVE` $\to$ `RESOLVED`).

### 7. Judge Calibration & Agreement Engine (Module G)
- **Cohen's Kappa ($\kappa$):** Unweighted $\kappa$ for binary dimensions; Linear/Quadratic Weighted $\kappa$ for ordinal 1-5 scales against human expert annotations.
- **Automated Gating Safety Lock:** Any judge with $\kappa < 0.70$ is barred from automated CI gatekeeping.
- **Confusion Matrices:** Evaluates sensitivity, specificity, false positive, and false negative rates.

### 8. Cryptographic Audit Trail & SR 11-7 Compliance (Module H)
- **Append-Only SHA-256 Hash Chaining:** Every governance event is chained:
  $$\text{record\_hash}_n = \text{SHA-256}(\text{previous\_hash}_{n-1} + \text{event\_type} + \text{payload} + \text{seq})$$
- **CLI Verification Command:** `python ci/veritas_audit.py` verifies mathematical chain continuity from genesis to head.
- **Regulatory Evidence Dossier:** Generates self-contained packages conforming to SR 11-7 / OCC 2011-12 with one-click JSON and CSV exports.

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- Python 3.12+
- Node.js v20+ / npm v10+
- PostgreSQL (Local or Docker)
- Optional: Google Gemini API Key (`GEMINI_API_KEY`)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/mishrasarthak08/LLM-Risk-Monitoring-Platform.git
cd LLM-Risk-Monitoring-Platform

# Install backend dependencies via uv / pip and frontend packages
make install
```

### 3. Environment Configuration
Create a `.env` file in the project root:
```ini
ENVIRONMENT=development
DATABASE_URL=postgresql+psycopg2://localhost:5432/veritas_ai_dev
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
GEMINI_API_KEY=your_gemini_api_key_here  # Optional: falls back to SimulatedProvider
DEFAULT_PROVIDER=simulated
```

### 4. Database Initialization & Demo Seeding
```bash
# Seed the database with commercial banking demonstration data
make seed-db
```
*Demo Credentials:* `admin@bank.com` / `VeritasAdmin2026!`

### 5. Launch the Platform
In Terminal 1 (FastAPI Backend on port 8000):
```bash
make backend
```
*API Documentation & Swagger UI:* [http://localhost:8000/docs](http://localhost:8000/docs)

In Terminal 2 (Celery Background Drift Worker):
```bash
make worker
```

In Terminal 3 (Next.js 14 Frontend on port 3000):
```bash
make frontend
```
*Web Application:* [http://localhost:3000](http://localhost:3000)

---

## 📦 Client SDKs

### Python SDK (`sdk/python`)
```bash
pip install ./sdk/python
```
```python
from veritas import Veritas

client = Veritas(
    api_key="vai_live_prod_...",
    base_url="http://localhost:8000/api/v1"
)

# Context manager with automatic child spans and client-side PII masking
with client.trace(feature_name="credit_memo_v1", input_payload={"loan_id": "LN-9821"}) as trace:
    with trace.span(name="llm_generation", span_type="LLM"):
        # Application LLM invocation
        pass
    trace.set_output("Application output text", status="SUCCESS")
```

### TypeScript SDK (`sdk/typescript`)
```typescript
import { VeritasClient } from "@veritas/sdk";

const veritas = new VeritasClient({
  apiKey: "vai_live_prod_...",
  baseUrl: "http://localhost:8000/api/v1"
});

await veritas.ingestTrace({
  featureName: "credit_memo_v1",
  inputPayload: { loan_id: "LN-9821" },
  outputText: "Classified assessment...",
  latencyMs: 420
});
```

---

## 🧪 Testing & Verification

Run the comprehensive Pytest verification suite (49 passing tests):
```bash
make test
```
*Test Coverage:*
- Multi-tenant data isolation & API key scoped authorization
- Python SDK async queue, timeout, jitter, and PII redactor
- Celery continuous drift worker execution
- Cryptographic hash-chain integrity & tamper detection
- Wilcoxon signed-rank paired tests & Cliff's Delta effect sizes
- Population Stability Index (PSI) & Kolmogorov-Smirnov detectors
- Two-proportion Z-tests & Cohen's Kappa evaluator agreement
- FastAPI REST API endpoints (health, projects, traces, prompts, regressions, drift, audit)

Run the Playwright browser end-to-end suite (11 passing tests):
```bash
make e2e
```

Run both test suites together:
```bash
make test-all
```

Verify the audit ledger via CLI:
```bash
make audit-verify
```

Run a headless CI regression evaluation:
```bash
make ci-regression
```

---

## 🏦 Compliance Mapping (Federal Reserve SR 11-7 / OCC 2011-12)

| SR 11-7 Regulatory Expectation | Platform System Control | Verification Artifact |
| :--- | :--- | :--- |
| **Ongoing Monitoring** | Continuous statistical drift detection (KS test, Z-test, PSI) running across rolling 24h traffic | `drift_events`, Drift Monitor Triage Desk |
| **Outcomes Analysis** | Versioned Golden Set regression evaluations with paired Wilcoxon signed-rank test | `regression_runs`, `regression_case_results` |
| **Process Verification & Benchmarking** | LLM-as-a-Judge evaluations calibrated against human ground truth via Cohen's Kappa | `calibration_runs`, `calibration_dimension_scores` |
| **Change Management** | Content-addressed immutable prompt versions and automated CI blocking gates | `prompt_versions`, `on_prompt_change.yml` |
| **Clear Accountability** | Named actor tracking across all actions (`actor_email`, `approved_by`) | `audit_events`, `audit_service.py` |
| **Audit Trail Integrity & Non-Repudiation** | Cryptographic SHA-256 hash-chaining across all immutable governance records | `audit_events.record_hash`, `ci/veritas_audit.py` |
| **Reporting to Stakeholders** | Multi-format regulatory dossier generation (JSON, CSV, PDF-ready) | `report_service.py`, `/reports` UI |

---

## 📄 License
MIT License. Developed for enterprise AI governance and reliability engineering.
