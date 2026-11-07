"""
VERITAS AI — Google Gemini Provider Adapter
Uses official google-genai SDK with exponential retry backoff.
"""
import os
import time
import asyncio
from typing import Optional, Any
from google import genai
from google.genai import types
from google.genai.errors import APIError

from backend.app.providers.base import BaseLLMProvider, GenerationResult
from backend.app.core.pricing import compute_cost_usd


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM Provider."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable or argument is required.")
        self.client = genai.Client(api_key=self.api_key)

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        **kwargs: Any
    ) -> GenerationResult:
        model = model_name or "gemini-2.5-flash"
        start_time = time.perf_counter()
        max_retries = 5
        base_delay = 2.0

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=system_instruction
        )

        for attempt in range(max_retries):
            try:
                # Wrap synchronous google-genai call in thread
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=config
                    )
                )

                latency_ms = int((time.perf_counter() - start_time) * 1000)
                output_text = response.text or ""

                usage_meta = getattr(response, "usage_metadata", None)
                in_tokens = getattr(usage_meta, "prompt_token_count", 0) if usage_meta else len(prompt.split()) * 2
                out_tokens = getattr(usage_meta, "candidates_token_count", 0) if usage_meta else len(output_text.split()) * 2
                tot_tokens = in_tokens + out_tokens

                cost = compute_cost_usd(model, in_tokens, out_tokens)

                return GenerationResult(
                    text=output_text,
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                    total_tokens=tot_tokens,
                    cost_usd=cost,
                    latency_ms=latency_ms,
                    error=None,
                    raw_response={"model": model, "usage": str(usage_meta)}
                )

            except APIError as e:
                if attempt == max_retries - 1:
                    latency_ms = int((time.perf_counter() - start_time) * 1000)
                    return GenerationResult(
                        text="",
                        error=f"Gemini API Error after {max_retries} attempts: {str(e)}",
                        latency_ms=latency_ms
                    )
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    await asyncio.sleep(base_delay * (2 ** attempt) + 5.0)
                else:
                    await asyncio.sleep(base_delay * (2 ** attempt))

            except Exception as e:
                latency_ms = int((time.perf_counter() - start_time) * 1000)
                return GenerationResult(
                    text="",
                    error=f"Unexpected error: {str(e)}",
                    latency_ms=latency_ms
                )

        return GenerationResult(text="", error="Exceeded maximum retries")

