# Architecture & First Principles

This document establishes the foundational architecture and non-negotiable engineering principles for the LLM Model-Risk Monitoring Platform. It acts as the source of truth for all subsequent phases to ensure compliance with model-risk governance requirements (SR 11-7 / OCC 2011-12).

## 1. The Four Architectural Decisions That Matter Most

These four rules separate a genuinely production-grade system from a simple evaluation wrapper:

1. **The golden set is a versioned, immutable artifact, never a live-edited table.**
   Any change to an expected answer creates a new immutable version with a content hash. Old versions are never deleted, ensuring every historical regression run explicitly records the exact golden-set version it ran against.
2. **The judge is validated against humans before it validates anything else.**
   The LLM-as-judge is treated as a component that must be validated. A stratified sample of judge scores is periodically checked against human-labeled scores, and inter-rater agreement is tracked over time.
3. **Regression and drift are different statistical questions, not the same feature twice.**
   Regression tests specific known cases and blocks CI. Drift monitors unknown production data for distributional shifts without blocking deployments.
4. **Every score traces back to an exact, reproducible lineage.**
   You must be able to answer what specific prompt version, model version, golden-set version, and judge version produced a score six months later. Lineage is tracked with explicit foreign keys.

## 2. Reference Architecture

The architecture consists of three core loops around one shared trace/evidence log:

- **Loop 1 — Production inference (the thing being watched):**
  Every call to the LLM feature is wrapped by a tracing decorator that writes a run record asynchronously. *Obligation: log everything, block on nothing.*
- **Loop 2 — Change-triggered regression (the CI gate):**
  A prompt/model change triggers a CI pipeline that runs the golden set through both new and baseline configs. The judge scores the outputs, and a pass/fail gate decision blocks or allows the deployment.
- **Loop 3 — Continuous drift monitoring (the early-warning system):**
  A scheduled job computes distributional statistics on production traffic over rolling windows, comparing them against a reference distribution to detect quiet quality shifts.

## 3. Non-Negotiable Engineering Principles

- **Append-only evidence tables:** No row in `run_traces`, `regression_runs`, `judge_scores`, or `drift_events` is ever UPDATEd or DELETEd.
- **Every artifact is content-hashed and versioned:** Golden sets, judge rubric prompts, and system prompts get a SHA-256 content hash computed at save time.
- **The judge is a monitored component, not an oracle:** Judge scores carry a `judge_version_id` and are subject to their own calibration monitoring.
- **Async logging never blocks user-facing latency:** Tracing writes happen on a background queue. If the DB is down, the feature must degrade gracefully without breaking.
- **Statistical thresholds are documented, not vibes:** Every drift threshold and regression pass/fail bar is written down with reasoning and versioned as config.
- **Human-in-the-loop is designed in, not bolted on:** Failure analysis and judge calibration have a human review UI/workflow from day one.
