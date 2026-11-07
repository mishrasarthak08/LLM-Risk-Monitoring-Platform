"""
VERITAS AI — Provider Factory
"""
import os
from typing import Optional
from backend.app.providers.base import BaseLLMProvider
from backend.app.providers.simulated import SimulatedProvider
from backend.app.core.config import settings


def get_llm_provider(
    provider_name: Optional[str] = None,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> BaseLLMProvider:
    name = (provider_name or settings.DEFAULT_PROVIDER).lower()

    if name in ("gemini", "google"):
        key = api_key or settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if key:
            try:
                from backend.app.providers.gemini import GeminiProvider
                return GeminiProvider(api_key=key)
            except Exception:
                pass
        # Fall back to simulated if no key is present
        return SimulatedProvider(model_name=model_name or "gemini-2.5-flash")

    # Default to simulated provider
    return SimulatedProvider(model_name=model_name or "simulated-model")

