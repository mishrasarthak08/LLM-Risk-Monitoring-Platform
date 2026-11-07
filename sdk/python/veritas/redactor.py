"""
VERITAS AI — Client-Side Sensitive Data Redactor
Redacts SSNs, payment card numbers, and API tokens before payload transmission.
"""
import re
from typing import Any, Dict, List, Union

SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CARD_REGEX = re.compile(r"\b(?:\d{4}[- ]?){3}\d{4}\b")
API_KEY_REGEX = re.compile(r"\b(?:sk-[a-zA-Z0-9]{20,}|vai_[a-zA-Z0-9_]{24,}|AIza[0-9A-Za-z-_]{35})\b")


def redact_string(val: str) -> str:
    val = SSN_REGEX.sub("[REDACTED_SSN]", val)
    val = CARD_REGEX.sub("[REDACTED_CARD]", val)
    val = API_KEY_REGEX.sub("[REDACTED_SECRET]", val)
    return val


def redact_payload(obj: Any) -> Any:
    if isinstance(obj, str):
        return redact_string(obj)
    elif isinstance(obj, dict):
        return {k: redact_payload(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [redact_payload(item) for item in obj]
    return obj

