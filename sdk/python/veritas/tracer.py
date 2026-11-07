"""
VERITAS AI — Trace and Span Context Handlers
"""
import time
import uuid
from typing import Any, Dict, List, Optional
from .redactor import redact_payload


class SpanContext:
    def __init__(self, name: str, span_type: str = "generic", parent_id: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.span_type = span_type
        self.parent_id = parent_id
        self.input_data: Optional[Dict[str, Any]] = None
        self.output_data: Optional[Dict[str, Any]] = None
        self.tokens: int = 0
        self.latency_ms: int = 0
        self.error_message: Optional[str] = None
        self._start_time: float = 0.0

    def __enter__(self):
        self._start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self._start_time
        self.latency_ms = max(1, int(duration * 1000))
        if exc_val:
            self.error_message = str(exc_val)
        return False  # Propagate exception to parent

    def log_input(self, data: Any):
        self.input_data = redact_payload(data)

    def log_output(self, data: Any):
        self.output_data = redact_payload(data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "span_type": self.span_type,
            "latency_ms": self.latency_ms,
            "tokens": self.tokens,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
        }


class TraceContext:
    def __init__(self, client: Any, feature_name: str, model_name: Optional[str] = None):
        self.client = client
        self.feature_name = feature_name
        self.model_name = model_name or "default-model"
        self.input_payload: Optional[Dict[str, Any]] = None
        self.output_text: Optional[str] = None
        self.input_tokens: int = 0
        self.output_tokens: int = 0
        self.latency_ms: int = 0
        self.status: str = "SUCCESS"
        self.error_message: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
        self.spans: List[SpanContext] = []
        self._start_time: float = 0.0

    def __enter__(self):
        self._start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self._start_time
        self.latency_ms = max(1, int(duration * 1000))
        if exc_val:
            self.status = "ERROR"
            self.error_message = str(exc_val)

        # Enqueue trace payload for delivery
        payload = self.to_dict()
        self.client.enqueue_trace(payload)
        return False  # Propagate exception

    def log_input(self, data: Any):
        self.input_payload = redact_payload(data)

    def log_output(self, data: Any):
        if isinstance(data, str):
            self.output_text = data
        else:
            self.output_text = str(redact_payload(data))

    def log_tokens(self, input_tokens: int, output_tokens: int):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens

    def log_metadata(self, meta: Dict[str, Any]):
        self.metadata.update(redact_payload(meta))

    def span(self, name: str, span_type: str = "generic") -> SpanContext:
        span_ctx = SpanContext(name=name, span_type=span_type)
        self.spans.append(span_ctx)
        return span_ctx

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feature_name": self.feature_name,
            "model_name": self.model_name,
            "input_payload": self.input_payload or {},
            "output_text": self.output_text or "",
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "latency_ms": self.latency_ms,
            "status": self.status,
            "error_message": self.error_message,
            "metadata_json": self.metadata or None,
            "spans": [s.to_dict() for s in self.spans]
        }

