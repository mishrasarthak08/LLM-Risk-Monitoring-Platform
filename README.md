# LLM Model-Risk Monitoring Platform

This project implements a production-grade LLM evaluation and observability platform designed to meet Federal Reserve SR 11-7 model-risk governance requirements. It monitors a simulated bank credit-memo drafting feature to ensure that its underlying LLM does not silently degrade in quality. The platform achieves this through a calibrated LLM-as-judge, a CI-blocking regression gate using paired Wilcoxon significance testing, and live statistical drift detection.

## Live Demo & Walkthrough

- **Live Dashboard**: [View Deployed Dashboard (Placeholder URL)](#)
- **Demo Video**:
  *(A 90-second screen recording showing a PR triggering the regression gate and the live dashboard reflecting a real trace will go here.)*

## Architecture

The architecture consists of three core loops built around one shared, append-only PostgreSQL evidence database:

```mermaid
flowchart TD
    %% Define Nodes
    subgraph "Loop 1: Production Inference"
        User[User / Application]
        Feature[Credit Memo Generator\n@traced_call]
        LLM[Anthropic API]
    end

    subgraph "Loop 2: Change-Triggered Regression (CI)"
        PR[Prompt / Model PR]
        Runner[Regression Runner]
        Judge[LLM-as-Judge]
        Wilcoxon[Wilcoxon Gate]
    end

    subgraph "Loop 3: Drift Monitoring"
        Scheduler[Drift Scheduler\n(Cron)]
        Stats[PSI / KS / Z-Tests]
        Alert[Slack Webhook]
    end

    DB[(PostgreSQL Evidence DB\nrun_traces, judge_scores,\nregression_runs, drift_events)]

    %% Loop 1 Connections
    User -->|Requests Memo| Feature
    Feature -->|Generates| LLM
    Feature -.->|Async Writes| DB

    %% Loop 2 Connections
    PR -->|Triggers| Runner
    Runner -->|Loads Golden Set| Judge
    Judge -->|Scores| Wilcoxon
    Wilcoxon -->|Pass/Block| PR
    Judge -.->|Async Writes| DB
    Wilcoxon -.->|Async Writes| DB

    %% Loop 3 Connections
    Scheduler -->|Reads| DB
    Scheduler -->|Computes| Stats
    Stats -->|Threshold Crossed| Alert
    Stats -.->|Async Writes| DB
```

## What's Actually Implemented

This project moves beyond simple "LLM wrappers" by implementing genuine statistical evaluation and monitoring:
- **Calibrated LLM-as-Judge**: The judge is evaluated against a human-labeled ground truth using Cohen's Kappa, proving it is a trustworthy rater before it is used to evaluate the core feature.
- **CI-Blocking Regression Gate**: Prompt changes trigger an automated regression suite across a versioned golden set. A paired Wilcoxon signed-rank test compares the baseline and candidate outputs, blocking the PR if quality has statistically degraded.
- **Production Drift Detection**: A cron job uses Population Stability Index (PSI), Kolmogorov-Smirnov (KS) tests, and two-proportion Z-tests to detect quiet distributional shifts in judge scores, output length, and refusal rates against a pinned baseline.
- **Async Tracing Pipeline**: Every LLM call is intercepted and recorded asynchronously (using a bounded queue and drop-oldest policy) with zero added latency, capturing full request lineage, tokens, and USD cost.

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/LLM-Risk-Monitoring-Platform.git
   cd LLM-Risk-Monitoring-Platform
   ```

2. **Set up your environment**:
   Copy the example environment file and fill in your keys (especially `ANTHROPIC_API_KEY`).
   ```bash
   cp .env.example .env
   ```

3. **Install dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Start the database and run migrations**:
   ```bash
   docker compose up -d
   alembic upgrade head
   ```

5. **Run the Dashboard**:
   ```bash
   streamlit run dashboard/streamlit_app/Home.py
   ```

## Design Decisions

- **Per-dimension judge calls over single combined calls**: The LLM judge scores five dimensions (e.g., Factual Accuracy, Tone) individually rather than outputting all five at once. This mitigates position and verbosity bias.
- **Wilcoxon test over a simple mean-difference threshold**: Because golden set scores are ordinal and non-normally distributed, the Wilcoxon signed-rank test is mathematically correct for determining if candidate scores are meaningfully worse than baseline scores, preventing noise from failing CI.
- **PSI for judge score drift**: Population Stability Index is used instead of mean shifting because it captures changes in the shape of the score distribution (e.g., if a model stops returning 5s and returns all 3s, even if the mean stays similar). Quantile jitter is applied to prevent degenerate bins.
- **Explicit Version Lineage**: The database strictly tracks `prompt_version_id`, `model_config_id`, and `judge_version_id` for every trace. This ensures that a score can be audited six months later and reproduced with certainty.
