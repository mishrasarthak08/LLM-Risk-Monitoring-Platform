import os
from monitoring.regression.runner import run_regression_suite
from monitoring.db.models import Base
from sqlalchemy import create_engine
os.environ["DATABASE_URL"] = "postgresql://dev_user:dev_password@localhost:5433/llm_monitoring_dev"

# Create DB schema if it doesn't exist
engine = create_engine(os.environ["DATABASE_URL"])
Base.metadata.create_all(engine)

print("Running regression suite to generate data...")
results = run_regression_suite(
    golden_set_path="monitoring/golden_set/data/v0002_credit_memo.jsonl",
    baseline_prompt_path="app/feature/prompts/credit_memo_v1.yaml",
    candidate_prompt_path="app/feature/prompts/credit_memo_v2.yaml",
    rubric_path="monitoring/judge/rubric/credit_memo_rubric_v2.yaml",
    repeats=1
)

print(f"Gate Decision: {results['gate_decision']['decision']}")
print(f"Reason: {results['gate_decision']['reason']}")
print("Done! Check dashboard.")
