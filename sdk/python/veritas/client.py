"""
VERITAS AI — Main Python Client & Background Ingestion Worker
"""
import atexit
import functools
import logging
import queue
import random
import threading
import time
from typing import Any, Callable, Dict, Optional
import urllib.request
import urllib.error
import json

from .tracer import TraceContext
from .exceptions import VeritasConfigurationError

logger = logging.getLogger("veritas")


class Veritas:
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: float = 5.0,
        max_retries: int = 3,
        sync_mode: bool = False,
    ):
        if not api_key:
            raise VeritasConfigurationError("VERITAS API key is required (e.g. vai_live_...).")

        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.sync_mode = sync_mode

        self._queue: queue.Queue = queue.Queue(maxsize=10000)
        self._stop_event = threading.Event()
        self._worker_thread: Optional[threading.Thread] = None

        if not self.sync_mode:
            self._start_worker()
            atexit.register(self.close)

    def _start_worker(self):
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True, name="VeritasWorker")
        self._worker_thread.start()

    def _worker_loop(self):
        while not self._stop_event.is_set():
            try:
                payload = self._queue.get(timeout=0.25)
            except queue.Empty:
                continue

            self._deliver_with_retry(payload)
            self._queue.task_done()

    def _deliver_with_retry(self, payload: Dict[str, Any]) -> bool:
        endpoint = f"{self.base_url}/traces/ingest"
        data_bytes = json.dumps(payload).encode("utf-8")

        for attempt in range(1, self.max_retries + 1):
            req = urllib.request.Request(
                endpoint,
                data=data_bytes,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key,
                    "User-Agent": "veritas-python-sdk/2.0.0"
                },
                method="POST"
            )

            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    if resp.status in (200, 201):
                        return True
            except urllib.error.HTTPError as e:
                # 4xx errors (e.g. 401, 400) should not retry blindly
                if 400 <= e.code < 500:
                    logger.error("VERITAS ingestion rejected [HTTP %d]: %s", e.code, e.read().decode("utf-8", "ignore"))
                    return False
            except Exception as e:
                logger.warning("VERITAS ingestion attempt %d/%d failed: %s", attempt, self.max_retries, e)

            # Exponential backoff with jitter
            if attempt < self.max_retries:
                sleep_time = (0.5 * (2 ** (attempt - 1))) + random.uniform(0.05, 0.2)
                time.sleep(sleep_time)

        logger.error("Failed to deliver trace to VERITAS after %d attempts.", self.max_retries)
        return False

    def enqueue_trace(self, payload: Dict[str, Any]):
        if self.sync_mode:
            self._deliver_with_retry(payload)
        else:
            try:
                self._queue.put_nowait(payload)
            except queue.Full:
                logger.warning("VERITAS trace buffer full (10,000 items). Dropping telemetry to protect application memory.")

    def trace(self, name: str, model_name: Optional[str] = None) -> TraceContext:
        """Context manager to instrument an LLM transaction."""
        return TraceContext(client=self, feature_name=name, model_name=model_name)

    def traced(self, feature_name: Optional[str] = None, model_name: Optional[str] = None):
        """Decorator to instrument a function call."""
        def decorator(func: Callable):
            fname = feature_name or func.__name__

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                with self.trace(name=fname, model_name=model_name) as t:
                    t.log_input({"args": [str(a) for a in args], "kwargs": kwargs})
                    result = func(*args, **kwargs)
                    t.log_output(result)
                    return result
            return wrapper
        return decorator

    def flush(self, timeout: float = 5.0):
        """Block until all buffered traces have been sent."""
        if not self.sync_mode and self._queue:
            start = time.perf_counter()
            while not self._queue.empty() and (time.perf_counter() - start < timeout):
                time.sleep(0.05)

    def close(self):
        """Gracefully flush and terminate background ingestion thread."""
        self.flush(timeout=3.0)
        self._stop_event.set()
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=1.0)

