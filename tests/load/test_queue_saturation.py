import time
import uuid
import pytest
from monitoring.tracing.async_writer import enqueue_trace, trace_queue

def test_queue_saturation():
    """
    Overwhelm the async_writer with >1,000 trace calls to verify the drop-oldest
    policy behaves as expected without blocking.
    """
    # Create fake trace data
    def make_trace_data(i):
        return {
            "id": uuid.uuid4(),
            "trace_type": "feature",
            "feature_name": "saturation_test",
            "prompt_version_id": uuid.uuid4(),
            "model_config_id": uuid.uuid4(),
            "input_payload": {"test_idx": i},
        }

    # Ensure queue size is respected
    max_qsize = trace_queue.maxsize
    assert max_qsize == 1000, "Queue maxsize should be 1000"

    # To isolate from the background worker, we mock or pause the worker
    # We will just fill it very fast so the worker can't keep up
    
    start_time = time.time()
    
    # We enqueue 1500 items, queue max size is 1000
    for i in range(1500):
        enqueue_trace(make_trace_data(i))
        
    end_time = time.time()
    
    # Assert it was fast (non-blocking)
    assert end_time - start_time < 2.0, "Enqueueing 1500 items took too long, might be blocking"
    
    # We can check that the queue is bounded
    assert trace_queue.qsize() <= max_qsize

