import queue
import threading
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from monitoring.db.models import RunTrace
from monitoring.utils.json_logger import setup_json_logger

logger = setup_json_logger(__name__)

# Bounded queue to avoid memory leaks
trace_queue: queue.Queue = queue.Queue(maxsize=1000)

_engine = None
_SessionLocal = None


def get_session():
    global _engine, _SessionLocal
    if _engine is None:
        db_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://dev_user:dev_password@localhost:5432/llm_monitoring_dev"
        )
        _engine = create_engine(db_url, pool_pre_ping=True)
        _SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=_engine
        )
    return _SessionLocal()


def worker():
    while True:
        try:
            trace_data = trace_queue.get()
            if trace_data is None:  # Sentinel to stop worker
                break

            with get_session() as session:
                trace_record = RunTrace(**trace_data)
                session.add(trace_record)
                session.commit()
        except Exception as e:
            # We swallow the error and log it to avoid breaking the background thread
            logger.error(f"Failed to write trace to DB: {e}")
            import time
            time.sleep(1)
            # Re-enqueue the trace for retry
            try:
                trace_queue.put_nowait(trace_data)
            except queue.Full:
                pass
        finally:
            if trace_data is not None:
                trace_queue.task_done()


# Start the background worker thread (daemon so it doesn't block exit)
writer_thread = threading.Thread(target=worker, daemon=True, name="writer_thread")
writer_thread.start()


def enqueue_trace(trace_data: dict):
    """
    Non-blocking enqueue with a drop-oldest policy on overflow.
    """
    try:
        trace_queue.put_nowait(trace_data)
    except queue.Full:
        try:
            # Drop oldest to make room
            trace_queue.get_nowait()
            trace_queue.put_nowait(trace_data)
            logger.warning("Trace queue full: dropped oldest trace.")
        except queue.Empty:
            # Queue was drained between Full and Empty, just put
            trace_queue.put_nowait(trace_data)
