# Runbook: Critical Drift Alert

**Trigger:** The automated Drift Scheduler has fired an alert to PagerDuty/Slack indicating a statistically significant distributional shift in live production traffic.

## Immediate Steps

1. **Acknowledge the Alert:**
   - Go to the Streamlit **Drift Monitor** dashboard.
   - Click "Acknowledge" on the open alert. This stops duplicate pages and starts the SLA triage clock.

2. **Investigate the Shift:**
   - Review the specific metric that shifted (e.g., `refusal_rate`, `output_length`, `judge_score_psi`).
   - Pull sample outputs from the drifted window (linked directly in the dashboard) and manually review them against the reference window.

3. **Rule Out Process Failures:**
   - Check if a prompt or model config change was shipped recently *without* going through the regression gate.
   - Check the LLM provider's status page and changelogs. Was the underlying model silently updated by the provider?

## Triage Outcomes

You must record one of the following outcomes in the Drift Monitor:

### Outcome A: Confirmed Quality Issue
The model's behavior has genuinely degraded on live traffic.
- **Action:** Open an Incident.
- **Action:** Consider an immediate rollback to a prior prompt/config if severe.
- **Action:** Extract the specific production payloads that failed, and add them to the Golden Set as `known_failure` cases (via the Failure Analysis Workbench) so this specific failure mode is permanently regression-tested.

### Outcome B: Benign Population Shift
Users are legitimately using the feature differently (e.g., uploading much larger documents, causing a shift in `output_length`), but the quality is still perfectly acceptable.
- **Action:** Approve a Reference Rebuild. This will snapshot the current traffic as the new baseline distribution.

### Outcome C: False Positive / Too Sensitive
The shift is mathematically real but practically irrelevant.
- **Action:** File a follow-up ticket to tune the thresholds in `config/thresholds.yaml` to make the detector less sensitive.
