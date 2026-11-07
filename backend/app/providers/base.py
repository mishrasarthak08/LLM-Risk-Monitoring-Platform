"""
VERITAS AI — Base Provider Interface
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class GenerationResult:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    error: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = field(default_factory=dict)


class BaseLLMProvider(ABC):
    """Abstract Base Class for all LLM Provider Adapters."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        **kwargs: Any
    ) -> GenerationResult:
        """Executes content generation asynchronously."""
        pass

