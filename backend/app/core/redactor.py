"""
VERITAS AI — Sensitive Data & PII Redactor
Prevents credential leaks and customer privacy violations in telemetry.
"""
import re
from typing import Any

# Regex patterns for high-risk sensitive strings
SSN_PATTERN = re.compile(r"\b\d{3}[-]?\d{2}[-]?\d{4}\b")
CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
API_KEY_PATTERN = re.compile(r"\b(?:vai_live_[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z-_]{35})\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")


def redact_string(text: str) -> str:
    """Redacts sensitive PII and secret patterns from text."""
    if not text or not isinstance(text, str):
        return text
    redacted = SSN_PATTERN.sub("[REDACTED_SSN]", text)
    redacted = API_KEY_PATTERN.sub("[REDACTED_API_KEY]", redacted)
    redacted = CREDIT_CARD_PATTERN.sub("[REDACTED_CARD]", redacted)
    return redacted


def sanitize_payload(payload: Any) -> Any:
    """Recursively walks dictionaries, lists, and strings to sanitize payloads."""
    if isinstance(payload, str):
        return redact_string(payload)
    elif isinstance(payload, dict):
        return {k: sanitize_payload(v) for k, v in payload.items()}
    elif isinstance(payload, list):
        return [sanitize_payload(item) for item in payload]
    return payload

