# Runbook: Regression Gate Blocked a Deploy

**Trigger:** The `LLM Regression Gate` CI job failed, preventing a merge to a protected branch.

## Immediate Steps

1. **Open the Linked Report:**
   - Locate the automated comment left by the CI bot on your Pull Request.
   - Click the link to view the generated Regression Report (or open Streamlit -> Regression History).

2. **Identify the Failure Mode:**
   - Look at the **Gate Decision** block. Did it fail due to:
     - `blocking-severity case(s) newly failing` (Even 1 is enough)
     - `major-severity cases newly failing (threshold: 3)`
     - `Statistically significant net score decline` (Wilcoxon test failure)

3. **Examine Specific Cases:**
   - In the Streamlit dashboard, go to the **Failure Analysis Workbench**.
   - Select the failed run.
   - For each `newly_failing` case, read the Judge Rationale for both the **Baseline (Passed)** and **Candidate (Failed)** outputs.

## Triage & Resolution

### Scenario A: Genuine Regression
The model output genuinely worsened due to your prompt/config change.

**Action:**
1. Fix your prompt or config in your branch.
2. Push the changes to trigger a new CI run.
3. Wait for the new run to pass before merging.

### Scenario B: Judge Miscalibration
The model output is actually fine (or better!), but the LLM Judge incorrectly flagged it as a failure because the Rubric is outdated or ambiguous.

**Action:**
1. Do **NOT** just bypass the gate.
2. Open the Streamlit **Judge Calibration Status** page.
3. If you believe the rubric is wrong, you must update the rubric (which bumps the `judge_version_id`), recalibrate it against human labels, and then re-run your CI.

### Scenario C: Acceptable Trade-off (Override Required)
The regression is real, but it is an accepted trade-off (e.g., we accept a slight drop in verbosity to fix a critical hallucination bug).

**Action:**
1. This requires explicit sign-off from a designated Model Risk or Compliance officer.
2. The override must be executed via the formal CI override path (logged to the database), never by temporarily turning off branch protection.
3. Document the exact reason for the override.
