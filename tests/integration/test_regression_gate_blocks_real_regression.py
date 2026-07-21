import json
from unittest.mock import patch, MagicMock

from monitoring.regression.runner import run_regression_suite

@patch("monitoring.regression.runner.run_feature_evaluation")
@patch("app.client.genai.Client")
def test_regression_gate_blocks_real_regression(mock_client_cls, mock_run_feature, tmp_path):
    """
    Asserts that if the candidate prompt produces outputs that score poorly,
    the gate_decision is 'block'.
    """
    # Create temporary files
    golden_path = tmp_path / "golden.jsonl"
    golden_path.write_text('{"category": "happy_path", "severity": "blocking", "input_payload": {}, "expected_criteria": {}, "case_hash": "abc", "source": "test", "added_by": "test", "added_at": "2026-01-01T00:00:00Z"}')

    base_prompt_path = tmp_path / "base.yaml"
    base_prompt_path.write_text("retrieve_docs: 'base docs'")

    cand_prompt_path = tmp_path / "cand.yaml"
    cand_prompt_path.write_text("retrieve_docs: 'cand docs'")

    rubric_path = tmp_path / "rubric.yaml"
    rubric_path.write_text('''
judge_model: "gemini-2.5-flash"
dimensions:
  - name: factual_accuracy
    prompt: "Is it accurate?"
''')

    # Mock feature evaluation so it doesn't actually call LLM
    def side_effect_feature(prompt_path, payload):
        if "base" in str(prompt_path):
            return "baseline output"
        return "candidate output"
    
    mock_run_feature.side_effect = side_effect_feature

    # Mock the Judge LLM
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    def side_effect_judge(model, contents, config=None, **kwargs):
        # We need to return a mocked message based on the input
        prompt_text = contents
        response = MagicMock()
        response.usage_metadata = MagicMock(prompt_token_count=10, candidates_token_count=10)
        
        # If it's evaluating baseline output, give it a 1 (pass)
        if "baseline output" in prompt_text:
            response.text = '{"score": 1, "rationale": "good"}'
        else:
            # Candidate gets a 0
            response.text = '{"score": 0, "rationale": "bad"}'
        return response

    mock_client.models.generate_content.side_effect = side_effect_judge

    results = run_regression_suite(
        golden_set_path=str(golden_path),
        baseline_prompt_path=str(base_prompt_path),
        candidate_prompt_path=str(cand_prompt_path),
        rubric_path=str(rubric_path)
    )

    gate = results["gate_decision"]
    assert gate["decision"] == "block"
    assert "blocking-severity case(s) newly failing" in gate["reason"]
