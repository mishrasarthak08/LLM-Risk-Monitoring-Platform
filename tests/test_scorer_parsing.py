from monitoring.judge.scorer import score_output


def test_score_output_parsing():
    rubric = {
        "judge_model": "mock-model",
        "dimensions": [
            {
                "name": "factual_accuracy",
                "prompt": "Score 1 if every numeric claim..."
            },
            {
                "name": "tone_clarity",
                "prompt": "Rate the tone and clarity..."
            }
        ]
    }

    source_data = {"revenue": 100}
    candidate_output = "The revenue is 100."

    results = score_output(rubric, source_data, candidate_output)

    assert len(results) == 2

    # Check first dimension
    fact_result = next(
        r for r in results if r["dimension"] == "factual_accuracy")
    assert fact_result["score"] == 1
    assert fact_result["error"] is None

    # Check second dimension
    tone_result = next(r for r in results if r["dimension"] == "tone_clarity")
    assert tone_result["score"] == 5
    assert tone_result["error"] is None


def test_score_output_json_error(monkeypatch):
    # Mock the LLM call to return invalid JSON
    monkeypatch.setattr("monitoring.judge.scorer._call_llm_judge",
                        lambda prompt, model: "This is not JSON")

    rubric = {
        "dimensions": [
            {
                "name": "test_dimension",
                "prompt": "Test prompt"
            }
        ]
    }

    results = score_output(rubric, {}, "test")
    assert len(results) == 1
    assert results[0]["score"] is None
    assert results[0]["error"] is not None
    assert "Expecting value" in results[0]["error"]
