# VERITAS AI — Product Gaps & Technical Debt Audit

## 1. Identified Architecture & Usability Gaps

### High Severity
1. **Legacy Test Database Inconsistencies (`tests/integration/`):**
   * *Issue:* 3 legacy test files in `tests/integration/` were still attempting to query `run_traces`, `judge_scores`, and old `prompt_versions` column definitions rather than the modern normalized `backend.app.models` schema.
   * *Remediation:* Modernize these integration test fixtures to target modern multi-tenant tables (`traces`, `drift_events`, `prompt_versions`).

2. **Provider Key Management (BYOK):**
   * *Issue:* Users could generate VERITAS API keys for their own apps, but could not configure their project-level external LLM provider keys (OpenAI API key, Anthropic API key, Google Gemini key) directly in the UI.
   * *Remediation:* Implement a dedicated "Provider Settings & BYOK" card in `/projects` with secure masked storage.

3. **Alert Webhook Dispatchers:**
   * *Issue:* When a drift incident is logged or an automated CI gate fails, incident records are saved in the DB, but outbound Slack/PagerDuty webhooks were not dispatched.
   * *Remediation:* Provide an outbound HTTP dispatcher service with HMAC signing and configurable webhook URLs in project settings.

### Medium Severity
4. **Contextual Deep-Linking:**
   * *Issue:* Navigating from an active Drift Incident alert on the dashboard did not pre-filter the Trace Explorer.
   * *Remediation:* Wire URL query params (`/traces?metric=output_length&status=ERROR`) to auto-populate the trace search bar.

5. **Empty State Guidance:**
   * *Issue:* Brand new projects with zero traces displayed blank `0.00` metrics with no call to action.
   * *Remediation:* Add empty state banners with one-click copyable SDK integration snippets and "Send Test Event" triggers.
