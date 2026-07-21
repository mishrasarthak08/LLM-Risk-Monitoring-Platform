# Portfolio Guide

This document is designed to help you present the LLM Model-Risk Monitoring Platform in interviews or to recruiters. It includes a script for recording a demo video, action-oriented resume bullets, and advice on how to discuss the project's evolution honestly and compellingly.

## Demo Video Script (90 seconds)

A short, recorded walkthrough is often the artifact most likely to be watched. Here is a suggested 90-second script:

- **[0:00–0:15] The Problem**: 
  "Banks need audit-grade evidence that an LLM feature didn't silently degrade in quality. This project is a production-grade LLM evaluation and observability platform designed to meet Federal Reserve SR 11-7 model-risk governance requirements."

- **[0:15–0:45] The CI Gate**: 
  *(Open a PR that changes a prompt for the worse in the code, for example, removing a DSCR instruction.)* 
  "Here, I'm opening a Pull Request that introduces a bad prompt change. The CI pipeline intercepts this, runs the prompt against a versioned golden set, and uses an LLM-as-judge calibrated against human labels. A paired Wilcoxon signed-rank test compares the new output against the baseline. The gate actively blocks the PR, as you can see in this GitHub comment showing the specific failing case."

- **[0:45–1:15] Live Observability & Drift**: 
  *(Flip to the live Streamlit dashboard.)*
  "In production, every LLM call is traced asynchronously with zero added latency, logging cost, tokens, and lineage. This live dashboard visualizes those traces. In the background, a cron job runs statistical tests—like Population Stability Index (PSI) and Kolmogorov-Smirnov (KS)—to detect quiet distributional shifts in output length or judge scores, alerting us to drift before users notice."

- **[1:15–1:30] Next Steps**: 
  "If I had more time, I would expand the golden set further and implement a shared external queue like Redis for cross-process tracing coordination, moving beyond the current single-process daemon thread."

## Resume Bullets

These bullets are grounded strictly in the verified architecture of the repository:

- Built an LLM evaluation and observability platform for a simulated bank credit-memo feature, implementing a calibrated LLM-as-judge (Cohen's Kappa against human-labeled ground truth) and a CI-blocking regression gate using paired Wilcoxon significance testing across a versioned golden test set.
- Designed a 12-table append-only PostgreSQL evidence schema with full lineage from prompt version through judge score to drift event, mapped explicitly to Federal Reserve SR 11-7 model-risk governance requirements.
- Implemented production drift detection using three complementary statistical tests (Population Stability Index, Kolmogorov-Smirnov, two-proportion Z-test) to separately monitor judge-score, output-length, and refusal-rate distributions against a pinned baseline.
- Built an async, non-blocking tracing pipeline capturing full request lineage, token usage, and cost per LLM call with zero added latency to the calling application, achieving 88%+ test coverage on core logic.

## How to Talk About This Honestly

**The honest version is the stronger version.**

This project's real strength—a genuinely correct statistical evaluation and drift-detection architecture—is more impressive than a system that quietly worked first try. A system that worked flawlessly on the first pass wouldn't need someone who understands why a Wilcoxon test is better than a simple mean-difference threshold, or why PSI bins need quantile jitter to avoid degenerate bins.

If an interviewer asks, *"What was hardest?"* or *"What would you do differently?"*, the true answer is exactly the finding at the center of Phase 9 of this project:

> "I designed and built the full evaluation architecture first, including the statistics and the schema. But when I wired in real model calls, I discovered my CI gate was fundamentally flawed—the mocked judge ignored the candidate output, and the CI workflow was comparing a file to itself. The hardest part was unraveling that stub chain, integrating the real signal, and proving that the gate actually failed on a bad prompt before I could trust it to pass a good one."

This is a genuinely good story. It is a defensible and common way real projects get built, and it demonstrates the ability to design a system correctly before all its parts exist—which is its own real skill.
