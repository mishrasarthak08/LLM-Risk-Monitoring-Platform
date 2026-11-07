# VERITAS AI — UX Research & User Journey Specifications

## 1. Primary User Personas

| Persona | Primary Goal | Critical Pain Point | Core Workflows Used |
| :--- | :--- | :--- | :--- |
| **AI Application Engineer** | Debug prompt chains, investigate unexpected model outputs, test changes before merge | Silent regressions, lack of span visibility in multi-step agents | Traces Explorer, Prompt Registry Diffing, Evaluation Studio |
| **ML & Platform Lead** | Ensure model reliability, evaluate provider transitions (e.g. GPT-4o to Claude 3.5 Sonnet / Gemini), monitor cost | Token spend explosions, uncalibrated LLM judges, distribution drift | Regression Gate, Drift Monitor, Judge Calibration, Analytics |
| **Model Risk & Compliance Officer** | Satisfy regulatory requirements (Federal Reserve SR 11-7 / OCC 2011-12), produce tamper-evident audit evidence | Unverifiable AI decisions, lack of versioned test suites, audit tampering | Cryptographic Audit Ledger, SR 11-7 Evidence Dossier, Golden Datasets |

---

## 2. Core Customer Journeys

### Journey 1: Discover → Onboard → Receive First Trace (Time to Value: < 5 Minutes)
1. **Discovery:** User lands on `/`, reads clear value proposition ("Enterprise LLM Reliability, Evaluation, Observability & Governance").
2. **Registration:** User creates an organization (`/register`) with work email and password.
3. **Onboarding Wizard:** Guided 4-step wizard (`/onboarding`):
   * Step 1: Workspace Setup (Org name, Project name).
   * Step 2: API Key Generation (Generates `vert_live_...` and copies to clipboard).
   * Step 3: SDK Integration (Interactive Python / TypeScript code snippet).
   * Step 4: Verification (User sends test event or clicks "Send Test Event", backend registers trace, wizard confirms with green checkmark).
4. **First Value:** User is taken directly to `/traces` to inspect their newly received execution trace.

### Journey 2: Prompt Update → CI Regression Check → Gate Decision
1. **Drafting:** Engineer edits prompt template in `/prompts`, previews variables, and commits changes.
2. **Pre-merge Testing:** In GitHub Actions CI, `python ci/veritas_ci.py` runs against the golden benchmark dataset.
3. **Statistical Analysis:** Engine compares candidate vs. baseline using the Wilcoxon signed-rank test and Cliff's Delta.
4. **Gate Resolution:** 
   * If any `blocking` test case fails $\to$ CI exits 1, PR is blocked.
   * Engineer visits `/regressions`, clicks into failed test case, reviews evaluator rationale and input/output diff, fixes the prompt, and re-runs.

### Journey 3: Production Drift Incident → Root Cause Triage
1. **Alerting:** Background monitor detects Kolmogorov-Smirnov shift ($p < 0.05$) in output length over rolling 24-hour window.
2. **Investigation:** Engineer opens `/drift`, selects the open incident.
3. **Contextual Drilldown:** Clicks "Inspect Affected Traces" which deep-links to `/traces?model=gpt-4o&time_window=24h`.
4. **Resolution:** Identifies an upstream schema change in client payload; updates incident status from `OPEN` to `CONFIRMED_ISSUE` and leaves notes in the triage log.

### Journey 4: Model Risk Review & Audit Verification
1. **Audit Check:** Risk Officer visits `/audit`, clicks "Verify SHA-256 Chain". System recalculates running hash from genesis block to head.
2. **Regulatory Package:** Officer navigates to `/reports`, selects the model and date window, reviews the automated SR 11-7 checklist, and downloads the cryptographically sealed JSON/CSV evidence dossier.
