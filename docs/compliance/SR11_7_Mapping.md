# SR 11-7 / OCC 2011-12 Evidence Mapping

The Federal Reserve's SR 11-7 (Supervisory Guidance on Model Risk Management) organizes model risk management around three pillars: robust model development, effective validation, and sound governance. 

This document serves as the literal mapping between the regulatory expectations and the specific technical artifacts produced by this LLM Risk Monitoring Platform.

| SR 11-7 Expectation | Platform System Artifact |
| :--- | :--- |
| **Ongoing monitoring** to confirm the model continues to perform as intended | Continuous drift detection (Phase 6 detectors) + change-triggered regression (Phase 5 runner), both writing to the append-only PostgreSQL evidence log (`run_traces`, `drift_events`). |
| **Outcomes analysis** comparing model output to expected/actual results | Golden-set regression comparisons (`regression_case_results`) with documented pass criteria per case, available in the Validation Report Generator. |
| **Process verification / benchmarking** against an independent challenge | LLM-as-judge scoring, which is itself validated against independent human review (Phase 4). The calibration record (`judge_versions.calibration_status` & Kappa scores) is the evidence that the challenger process is mathematically sound. |
| **Documentation sufficient** for an independent party to understand limitations | Golden-set case documentation (`notes` field, `category`, `source`), rubric YAML with explicitly documented aggregation logic, and `thresholds.yaml` with documented statistical reasoning per threshold. |
| **Change management** — review and approval before implementation | Golden-set version governance workflow (Phase 3), CI regression gate with logged, named override process (Phase 5). |
| **Clear roles and accountability** for validation activities | `approved_by` / `acknowledged_by` fields throughout the PostgreSQL schema, explicitly mapped to real human reviewer identities rather than service accounts. |
| **Reporting to senior management** and other stakeholders | Streamlit Validation Report Generator (Phase 7) — self-contained, date-ranged PDF evidence packages. |

## Data Access & Integrity

To satisfy the evidentiary requirements of the audit trail:
- Evidence tables (`run_traces`, `judge_scores`, `regression_runs`, `drift_events`) are strictly **append-only**.
- No human, including engineers with production DB access, has standing `UPDATE`/`DELETE` grants on these tables.
- All Read access is logged via `pgaudit`.
