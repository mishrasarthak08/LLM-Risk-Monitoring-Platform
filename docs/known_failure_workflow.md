# Known Failure Workflow

This document explains the process for converting a production failure into a permanent, regression-tested `known_failure` golden-set case.

## Why this is required
"Known failures" are the highest-value regression cases. Every time a model hallucination, unsafe refusal, or logic failure slips into production, catching it isn't enough. We must guarantee that *this specific failure mode* is never reintroduced silently by a future prompt change. By adding it to the golden set, the system accumulates institutional memory of its own mistakes.

## Workflow

1. **Identify the Failure**: 
   A failure is identified through human review in the Phase 7 Failure Analysis Workbench, a user-reported bug, or an escalating drift alert (Phase 6).
2. **Find the Trace**:
   Obtain the `trace_id` of the failed inference from the `run_traces` table. Use the Streamlit Run Explorer to pull the exact input payload, expected output (what *should* have happened), and the model's actual bad response.
3. **Format the Case**:
   Open a new PR against the `monitoring/golden_set/data/` directory. You will create a new JSONL version of the golden set.
   Append the new case to the JSONL file. 
   - Set `category` to `"known_failure"`.
   - Set `source` to `"production_incident:<trace_id>"`.
   - Fill in `expected_criteria` carefully to target the exact reason it failed.
   - **Crucial**: Provide a detailed explanation in the `notes` field documenting *why* this case was added and what went wrong in production.
4. **Submit for Review**:
   Open a PR. The GitHub action will automatically diff the golden set and post a summary. 
5. **Approval**:
   A model-risk or compliance reviewer (e.g., someone with the domain expertise to confirm the pass criteria) must approve the PR. This becomes the `approved_by` record for that version.
6. **Merge**:
   Once merged, all subsequent CI regression runs will test every new prompt or model change against this incident, ensuring the model never forgets the fix.
