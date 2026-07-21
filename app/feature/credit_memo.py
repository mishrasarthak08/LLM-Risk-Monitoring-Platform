from app.client import call_llm
from monitoring.tracing.decorators import traced_call


@traced_call(feature_name="credit_memo_drafting", trace_type="production")
def retrieve_documents(*args, **kwargs) -> tuple[str, dict]:
    prompt = kwargs.get("prompt_template", "retrieve docs")
    return call_llm(prompt, kwargs.get("model_config", {}))


@traced_call(feature_name="credit_memo_drafting", trace_type="production")
def draft_memo(*args, **kwargs) -> tuple[str, dict]:
    prompt = kwargs.get("prompt_template", "Draft memo from docs")
    return call_llm(prompt, kwargs.get("model_config", {}))


@traced_call(feature_name="credit_memo_drafting", trace_type="production")
def check_memo(*args, **kwargs) -> tuple[str, dict]:
    prompt = kwargs.get("prompt_template", "check memo")
    return call_llm(prompt, kwargs.get("model_config", {}))


@traced_call(feature_name="credit_memo_drafting", trace_type="production")
def generate_credit_memo(*args, **kwargs) -> tuple[str, dict]:
    """
    Multi-step chain: retrieve docs -> draft memo -> check memo.
    """
    prompts = kwargs.get("prompts", {})
    
    _ = retrieve_documents(
        prompt_template=prompts.get("retrieve_docs", "Find W2s"), 
        model_config=kwargs.get("model_config"))

    # Outer traced draft call
    output = draft_memo(
        prompt_template=prompts.get("draft_memo", "Draft memo from docs"), 
        model_config=kwargs.get("model_config", {}))

    # Inner traced check call
    check = check_memo(
        prompt_template=prompts.get("check_memo", "Verify policy"),
        model_config=kwargs.get("model_config"))

    return f"{output}\n{check}", {}
