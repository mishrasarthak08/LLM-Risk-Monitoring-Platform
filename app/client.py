import os
import time
import json
import hashlib
from google import genai
from google.genai import types
from google.genai.errors import APIError

MAX_LLM_CALLS_PER_RUN = 1000
_call_count = 0
_cache = {}

def call_llm(prompt: str, model_config: dict) -> tuple[str, dict]:
    global _call_count
    
    # Check cache first
    config_hash = hashlib.sha256(json.dumps(model_config, sort_keys=True).encode()).hexdigest()
    cache_key = hashlib.sha256(f"{prompt}:{config_hash}".encode()).hexdigest()
    
    if cache_key in _cache:
        return _cache[cache_key]
        
    if _call_count >= MAX_LLM_CALLS_PER_RUN:
        raise Exception(f"Exceeded hard limit of {MAX_LLM_CALLS_PER_RUN} LLM calls per run")
        
    _call_count += 1
    
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    model_name = model_config.get("model_name", "gemini-2.5-flash")
    
    max_retries = 5
    base_delay = 5.0
    
    for attempt in range(max_retries):
        try:
            config = types.GenerateContentConfig(
                max_output_tokens=model_config.get("max_tokens", 1024),
            )
            if "temperature" in model_config:
                config.temperature = model_config["temperature"]
                
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )
            
            output = response.text
            usage_metadata = getattr(response, "usage_metadata", None)
            if usage_metadata:
                usage = {
                    "input_tokens": getattr(usage_metadata, "prompt_token_count", 0),
                    "output_tokens": getattr(usage_metadata, "candidates_token_count", 0)
                }
            else:
                usage = {"input_tokens": 0, "output_tokens": 0}
            
            _cache[cache_key] = (output, usage)
            
            # Small sleep to respect RPM limits on Gemini Free Tier
            time.sleep(2.0)
            
            return output, usage
            
        except APIError as e:
            if attempt == max_retries - 1:
                raise e
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                time.sleep(15.0)
            else:
                time.sleep(base_delay * (2 ** attempt))
