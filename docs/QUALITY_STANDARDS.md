# VERITAS AI — Engineering Quality & Acceptance Standards

## 1. Acceptance Gates

Every feature and route in VERITAS AI must satisfy eight strict acceptance gates prior to production release:

1. **Gate 1: Functional Correctness**
   * All API requests must return valid JSON matching Pydantic v2 schemas.
   * Zero synthetic mock fallbacks when connecting to backend endpoints.
2. **Gate 2: UX Completeness**
   * Loading skeletons on all asynchronous data fetches.
   * Actionable empty states with copyable SDK snippets when no data exists.
   * Clear error boundaries preventing blank-screen crashes.
3. **Gate 3: Data Integrity & Traceability**
   * Token counts and costs must never evaluate to negative values or NaN.
   * All prompt and dataset releases must have deterministic SHA-256 hashes.
4. **Gate 4: Security & Tenant Isolation**
   * Every SQL query MUST enforce `WHERE org_id = current_user.org_id` or `WHERE project_id = current_project.id`.
   * PII and API keys must be scrubbed before database commitment.
5. **Gate 5: Visual Excellence & Design Consistency**
   * Consistent semantic color tokens (`#3b82f6` primary, `#10b981` success, `#ef4444` danger, `#f59e0b` warning).
   * WCAG 2.2 Level AA contrast ratios on text and controls.
6. **Gate 6: Accessibility**
   * Full keyboard navigation (Tab, Arrow keys, Enter, Escape).
   * Screen-reader accessible buttons, modal dialog traps, and semantic labels.
7. **Gate 7: Performance Budgets**
   * Next.js production initial JS bundle < 120 kB shared.
   * API endpoints return in < 50ms for indexed relational queries.
8. **Gate 8: Automated Verification**
   * 100% pass rate across Pytest unit & statistical tests.
   * 100% pass rate across Playwright browser end-to-end tests.
