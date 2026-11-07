# VERITAS AI — Complete UI Inventory & Route Catalog

## 1. Public Marketing Website
* **Route:** `/`
* **Components:**
  * Navigation Bar with brand logo, product pill links, docs link, Sign In, and "Start Free Trial" CTA.
  * Hero Section with live-rendered interactive Product Inspector preview.
  * Interactive Product Capability Tabs: Trace Inspector, Prompt Diffs, Regression Gate, Drift Monitor, Calibration Matrix, Cryptographic Audit.
  * Value Proposition Grid: "Engineered for SR 11-7 & Enterprise LLM Workloads".
  * Technical Credibility & Architecture Diagram.
  * Trust & Security Standards (SOC 2 Type II controls, AES-256-GCM, SHA-256 chaining).
  * Conversion Footer with links to API Docs, SDKs, Compliance Guides, and Terms.

---

## 2. Authentication & Onboarding
* **`/login`:** Secure authentication with email/password, password visibility toggle (`Eye`/`EyeOff`), and session token persistence.
* **`/register`:** Self-service organization onboarding with company name, slug conflict resolution, and immediate redirect to onboarding.
* **`/onboarding`:** Multi-step setup wizard with live API key creation, copyable SDK commands, and backend handshake verification.

---

## 3. Authenticated Enterprise Application Shell

### Functional Navigation Hierarchy
* **WORKSPACE:**
  * `Overview` (`/dashboard`): High-level KPI metrics, active incidents, regression gate status, volume, and cost trends.
  * `Projects` (`/projects`): Multi-project workspace management, API keys, provider BYOK settings, and webhooks.
* **OBSERVABILITY:**
  * `Traces` (`/traces`): Distributed trace search, multi-filter query bar, span latency waterfall, and PII redaction inspector.
  * `Analytics` (`/reports` or `/analytics`): Token consumption, cost-by-model distributions, latency percentiles (P50, P90, P99).
* **QUALITY:**
  * `Evaluations` (`/evaluations`): Multi-criteria test runner, assertion validator, isolated LLM judge execution.
  * `Datasets` (`/datasets`): Golden benchmark collections, JSONL import, test case severity tagging (`blocking`, `major`, `minor`).
  * `Prompts` (`/prompts`): Prompt template registry, content-addressable SHA-256 versioning, unified visual diffing.
  * `Regression Tests` (`/regressions`): Automated candidate vs. baseline distribution testing with Wilcoxon signed-rank and Cliff's Delta.
* **RELIABILITY:**
  * `Drift Monitoring` (`/drift`): Continuous 24h rolling drift detection (PSI, KS test, 2-prop Z test) and incident triage workbench.
* **GOVERNANCE:**
  * `Judge Calibration` (`/calibration`): Cohen's Kappa ($\kappa$) inter-rater reliability studio, confusion matrix, and gating locks.
  * `Cryptographic Audit` (`/audit`): Tamper-evident SHA-256 chained transaction ledger with instant verification.
  * `Governance Dossier` (`/reports`): Federal Reserve SR 11-7 / OCC 2011-12 compliance reporting and audit export package.
