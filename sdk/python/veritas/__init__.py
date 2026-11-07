"""
VERITAS AI — Official Python SDK
Enterprise Reliability, Observability, and Governance for LLM Applications.
"""
from .client import Veritas
from .tracer import TraceContext, SpanContext
from .exceptions import VeritasException, VeritasConfigurationError, VeritasIngestionError

__version__ = "2.0.0"
__all__ = ["Veritas", "TraceContext", "SpanContext", "VeritasException", "VeritasConfigurationError", "VeritasIngestionError"]

