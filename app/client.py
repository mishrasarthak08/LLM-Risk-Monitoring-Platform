import time


def mock_llm_call(prompt: str, model_config: dict) -> tuple[str, dict]:
    """
    Mock LLM provider call that returns a tuple of (output_text, usage_dict).
    """
    time.sleep(0.1)  # Simulate network latency
    output = f"Mocked response for prompt: {prompt[:20]}..."
    usage = {
        "input_tokens": len(prompt) // 4,
        "output_tokens": 15
    }
    return output, usage
