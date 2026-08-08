CREATE TABLE prompt_versions (
    id UUID PRIMARY KEY,
    feature_name TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    version_label TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT NOT NULL,
    git_commit_sha TEXT
);

CREATE TABLE model_configs (
    id UUID PRIMARY KEY,
    provider TEXT NOT NULL,
    model_name TEXT NOT NULL,
    temperature NUMERIC,
    max_tokens INTEGER,
    other_params JSONB,
    content_hash TEXT NOT NULL
);

CREATE TABLE golden_set_versions (
    id UUID PRIMARY KEY,
    version_number INTEGER NOT NULL,
    feature_name TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    case_count INTEGER NOT NULL,
    storage_uri TEXT NOT NULL,
    change_summary TEXT NOT NULL,
    approved_by TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE golden_set_cases (
    id UUID PRIMARY KEY,
    golden_set_version_id UUID NOT NULL REFERENCES golden_set_versions(id),
    case_hash TEXT NOT NULL,
    category TEXT NOT NULL,
    input_payload JSONB NOT NULL,
    expected_output TEXT,
    expected_criteria JSONB,
    severity TEXT NOT NULL,
    tags TEXT[],
    source TEXT NOT NULL,
    added_by TEXT NOT NULL,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT NOT NULL
);

CREATE TABLE run_traces (
    id UUID PRIMARY KEY,
    trace_type TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    prompt_version_id UUID NOT NULL REFERENCES prompt_versions(id),
    model_config_id UUID NOT NULL REFERENCES model_configs(id),
    golden_set_version_id UUID REFERENCES golden_set_versions(id),
    input_payload JSONB NOT NULL,
    output_text TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_usd NUMERIC(12,6),
    latency_ms INTEGER,
    request_id TEXT,
    parent_span_id UUID,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE judge_versions (
    id UUID PRIMARY KEY,
    rubric_content_hash TEXT NOT NULL,
    rubric_text TEXT NOT NULL,
    judge_model_config_id UUID NOT NULL REFERENCES model_configs(id),
    calibration_status TEXT NOT NULL,
    last_kappa_score NUMERIC,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE judge_scores (
    id UUID PRIMARY KEY,
    run_trace_id UUID NOT NULL REFERENCES run_traces(id),
    judge_version_id UUID NOT NULL REFERENCES judge_versions(id),
    dimension TEXT NOT NULL,
    score NUMERIC NOT NULL,
    rationale TEXT NOT NULL,
    raw_judge_response JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE regression_runs (
    id UUID PRIMARY KEY,
    trigger TEXT NOT NULL,
    baseline_prompt_version_id UUID NOT NULL REFERENCES prompt_versions(id),
    candidate_prompt_version_id UUID NOT NULL REFERENCES prompt_versions(id),
    baseline_model_config_id UUID NOT NULL REFERENCES model_configs(id),
    candidate_model_config_id UUID NOT NULL REFERENCES model_configs(id),
    golden_set_version_id UUID NOT NULL REFERENCES golden_set_versions(id),
    judge_version_id UUID NOT NULL REFERENCES judge_versions(id),
    status TEXT NOT NULL,
    summary_stats JSONB,
    gate_decision TEXT,
    report_uri TEXT,
    ci_run_url TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE regression_case_results (
    id UUID PRIMARY KEY,
    regression_run_id UUID NOT NULL REFERENCES regression_runs(id),
    golden_set_case_id UUID NOT NULL REFERENCES golden_set_cases(id),
    baseline_run_trace_id UUID NOT NULL REFERENCES run_traces(id),
    candidate_run_trace_id UUID NOT NULL REFERENCES run_traces(id),
    baseline_score NUMERIC NOT NULL,
    candidate_score NUMERIC NOT NULL,
    delta NUMERIC NOT NULL,
    case_verdict TEXT NOT NULL,
    error_pattern TEXT
);

CREATE TABLE drift_reference_distributions (
    id UUID PRIMARY KEY,
    feature_name TEXT NOT NULL,
    metric TEXT NOT NULL,
    distribution_summary JSONB NOT NULL,
    built_from_window TSTZRANGE NOT NULL,
    superseded_by UUID REFERENCES drift_reference_distributions(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE drift_events (
    id UUID PRIMARY KEY,
    feature_name TEXT NOT NULL,
    metric TEXT NOT NULL,
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    reference_distribution_id UUID REFERENCES drift_reference_distributions(id),
    statistic_value NUMERIC NOT NULL,
    threshold NUMERIC NOT NULL,
    severity TEXT NOT NULL,
    sample_size INTEGER NOT NULL,
    acknowledged_by TEXT,
    acknowledged_at TIMESTAMPTZ,
    resolution_note TEXT
);

CREATE INDEX idx_run_traces_feature ON run_traces(feature_name);
CREATE INDEX idx_run_traces_created_at ON run_traces(created_at);
CREATE INDEX idx_drift_events_feature ON drift_events(feature_name);
CREATE INDEX idx_drift_events_window_start ON drift_events(window_start);
CREATE INDEX idx_judge_scores_run_trace_id ON judge_scores(run_trace_id);
