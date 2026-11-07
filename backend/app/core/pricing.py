"""
VERITAS AI — Model Pricing & Cost Accounting
"""
import os
import yaml
from typing import Dict, Any, Optional

DEFAULT_MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gemini-2.5-flash": {"input_cost_per_1k": 0.000075, "output_cost_per_1k": 0.0003},
    "gemini-1.5-pro": {"input_cost_per_1k": 0.00125, "output_cost_per_1k": 0.005},
    "gpt-4o": {"input_cost_per_1k": 0.005, "output_cost_per_1k": 0.015},
    "gpt-4o-mini": {"input_cost_per_1k": 0.00015, "output_cost_per_1k": 0.0006},
    "claude-3-5-sonnet": {"input_cost_per_1k": 0.003, "output_cost_per_1k": 0.015},
    "claude-3-haiku": {"input_cost_per_1k": 0.00025, "output_cost_per_1k": 0.00125},
    "simulated-model": {"input_cost_per_1k": 0.00005, "output_cost_per_1k": 0.00015},
}

_pricing_cache: Optional[Dict[str, Dict[str, float]]] = None


def get_pricing_table() -> Dict[str, Dict[str, float]]:
    global _pricing_cache
    if _pricing_cache is not None:
        return _pricing_cache

    pricing = DEFAULT_MODEL_PRICING.copy()
    config_path = os.getenv("PRICING_CONFIG_PATH", "config/model_pricing.yaml")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and "models" in data:
                    pricing.update(data["models"])
        except Exception:
            pass

    _pricing_cache = pricing
    return _pricing_cache


def compute_cost_usd(model_name: str, input_tokens: int, output_tokens: int) -> float:
    """Computes exact USD dollar cost based on token counts."""
    pricing_table = get_pricing_table()
    # Match exact or prefix
    matched = pricing_table.get(model_name)
    if not matched:
        for k, v in pricing_table.items():
            if k in model_name or model_name in k:
                matched = v
                break
    if not matched:
        matched = {"input_cost_per_1k": 0.0001, "output_cost_per_1k": 0.0003}

    valid_in = max(0, int(input_tokens or 0))
    valid_out = max(0, int(output_tokens or 0))
    in_cost = (valid_in / 1000.0) * matched.get("input_cost_per_1k", 0.0)
    out_cost = (valid_out / 1000.0) * matched.get("output_cost_per_1k", 0.0)
    return round(in_cost + out_cost, 6)

