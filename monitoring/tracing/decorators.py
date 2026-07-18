import time
import functools
import uuid
import yaml
import os
import logging
from typing import Callable

from monitoring.tracing.async_writer import enqueue_trace, get_session
from monitoring.tracing.span_context import get_parent_span_id, set_parent_span_id, reset_parent_span_id
from monitoring.db.models import PromptVersion, ModelConfig

logger = logging.getLogger(__name__)

# Simple cache for pricing
PRICING_CONFIG = None


def load_pricing():
    global PRICING_CONFIG
    if PRICING_CONFIG is None:
        path = os.path.abspath(os.path.join(os.path.dirname(
            __file__), '../../config/model_pricing.yaml'))
        if os.path.exists(path):
            with open(path, 'r') as f:
                PRICING_CONFIG = yaml.safe_load(f).get("models", {})
        else:
            PRICING_CONFIG = {}
    return PRICING_CONFIG


def compute_cost(model_name: str, usage: dict) -> float:
    pricing = load_pricing()
    model_pricing = pricing.get(
        model_name, {"input_cost_per_1k": 0, "output_cost_per_1k": 0})
    input_cost = (usage.get("input_tokens", 0) / 1000.0) * \
        model_pricing.get("input_cost_per_1k", 0)
    output_cost = (usage.get("output_tokens", 0) / 1000.0) * \
        model_pricing.get("output_cost_per_1k", 0)
    return input_cost + output_cost


def resolve_prompt_version(feature_name: str, prompt_template: str) -> uuid.UUID:
    with get_session() as session:
        prompt = session.query(PromptVersion).filter_by(
            feature_name=feature_name).first()
        if not prompt:
            from monitoring.golden_set.versioning import content_hash
            prompt = PromptVersion(
                id=uuid.uuid4(),
                feature_name=feature_name,
                content_hash=content_hash(prompt_template or ""),
                prompt_text=prompt_template or "",
                version_label="v1",
                created_by="system"
            )
            session.add(prompt)
            session.commit()
        return prompt.id


def resolve_model_config(model_config: dict) -> uuid.UUID:
    with get_session() as session:
        model_name = model_config.get("model_name", "unknown")
        config = session.query(ModelConfig).filter_by(
            model_name=model_name).first()
        if not config:
            from monitoring.golden_set.versioning import content_hash
            config = ModelConfig(
                id=uuid.uuid4(),
                provider=model_config.get("provider", "openai"),
                model_name=model_name,
                content_hash=content_hash(model_config)
            )
            session.add(config)
            session.commit()
        return config.id


def traced_call(feature_name: str, trace_type: str = "production"):
    """
    Wrap any function that makes an LLM provider call.
    Captures everything needed for the run_traces row and enqueues it.
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, prompt_template=None, model_config=None, **kwargs):
            trace_id = uuid.uuid4()
            parent_span_id = get_parent_span_id()

            # Start a new context for children spans
            token = set_parent_span_id(trace_id)

            try:
                # In production, these should be cached or pre-resolved to avoid DB hits on the critical path.
                prompt_version_id = resolve_prompt_version(
                    feature_name, prompt_template)
                model_config_id = resolve_model_config(model_config or {})
                model_name = (model_config or {}).get("model_name", "unknown")
            except Exception as e:
                logger.warning(f"Failed to resolve DB foreign keys: {e}")
                prompt_version_id = uuid.uuid4()
                model_config_id = uuid.uuid4()
                model_name = "unknown"

            start = time.perf_counter()
            error = None
            output = None
            usage = {}

            try:
                # The wrapped function must return a tuple (output, usage_dict)
                output, usage = fn(
                    *args, prompt_template=prompt_template, model_config=model_config, **kwargs)
            except Exception as e:
                error = str(e)
                raise
            finally:
                latency_ms = int((time.perf_counter() - start) * 1000)

                # Enqueue the trace asynchronously
                enqueue_trace({
                    "id": trace_id,
                    "trace_type": trace_type,
                    "feature_name": feature_name,
                    "prompt_version_id": prompt_version_id,
                    "model_config_id": model_config_id,
                    "golden_set_version_id": kwargs.get("golden_set_version_id"),
                    "input_payload": kwargs.get("rendered_input", {}),
                    "output_text": output,
                    "input_tokens": usage.get("input_tokens"),
                    "output_tokens": usage.get("output_tokens"),
                    "cost_usd": compute_cost(model_name, usage),
                    "latency_ms": latency_ms,
                    "parent_span_id": parent_span_id,
                    "error": error,
                })

                # Restore the parent span for the outer context
                reset_parent_span_id(token)

            return output
        return wrapper
    return decorator
