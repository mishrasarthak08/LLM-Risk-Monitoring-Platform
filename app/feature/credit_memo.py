from app.client import mock_llm_call
from monitoring.tracing.decorators import traced_call


@traced_call(feature_name="credit_memo_drafting", trace_type="production")
def retrieve_documents(*args, **kwargs) -> tuple[str, dict]:
    prompt = kwargs.get("prompt_template", "retrieve docs")
    return mock_llm_call(prompt, kwargs.get("model_config", {}))


@traced_call(feature_name="credit_memo_drafting", trace_type="production")
def check_memo(*args, **kwargs) -> tuple[str, dict]:
    prompt = kwargs.get("prompt_template", "check memo")
    return mock_llm_call(prompt, kwargs.get("model_config", {}))


@traced_call(feature_name="credit_memo_drafting", trace_type="production")
def generate_credit_memo(*args, **kwargs) -> tuple[str, dict]:
    """
    Multi-step chain: retrieve docs -> draft memo -> check memo.
    """
    _ = retrieve_documents(
        prompt_template="Find W2s", model_config=kwargs.get("model_config"))

    # Outer mock call
    output, u2 = mock_llm_call(
        "Draft memo from docs", kwargs.get("model_config", {}))

    # Inner mock call
    check = check_memo(prompt_template="Verify policy",
                       model_config=kwargs.get("model_config"))

    return f"{output}\n{check}", u2
