# Runbook: Judge Failed Recalibration

**Trigger:** The Judge Calibration CI job failed, or the Streamlit dashboard shows the Judge as `failed_calibration` or `stale`. Regression gating is now blocked for all engineers.

## Immediate Steps

1. **Verify Block Status:**
   - Confirm that the current `judge_versions.calibration_status` is correctly preventing any new CI regression runs from passing. A stale judge cannot be used as an automated gate.

2. **Enable Fallback (If Necessary):**
   - If engineering velocity is blocked and deploys *must* happen, update the configuration to fall back to the `last-known-good` calibrated `judge_version_id` for interim regression runs, provided the rubric hasn't materially changed.

## Investigation

Why did the judge fail calibration?

1. **Silent Model Update:** Has the underlying judge model (e.g., `gpt-4o`) been silently updated by the provider? This often causes subtle shifts in leniency or reasoning style.
2. **New Edge Cases:** Has the Golden Set grown to include highly complex edge cases that the current rubric doesn't instruct the judge on how to handle properly?
3. **Ambiguous Rubric:** Look at the specific dimensions where the Judge-Human Cohen's Kappa score dropped. Are the instructions for that dimension vague?

## Resolution

1. **Update the Rubric:** If the rubric is ambiguous, improve the prompt instructions in `monitoring/judge/rubric/*.yaml`.
2. **Re-run Calibration:** You must draw a *fresh* stratified sample of human-labeled cases. Do not overfit the rubric to the same stale sample.
3. **Approve New Judge:** Once the Kappa scores cross the required thresholds, mark the new judge version as `calibrated`. Gating is restored.
