import time
from unittest.mock import patch, MagicMock
from app.feature.credit_memo import retrieve_documents, generate_credit_memo


@patch('app.client.genai.Client')
def test_kill_the_db_resilience(mock_client_cls):
    """
    If the DB connection fails during resolving foreign keys,
    the decorator should still return the output quickly without throwing to the user.
    """
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.text = "Output"
    mock_response.usage_metadata = MagicMock(prompt_token_count=10, candidates_token_count=5)
    mock_client.models.generate_content.return_value = mock_response

    start = time.perf_counter()
    # Mocking the session resolver to simulate a DB failure
    with patch('monitoring.tracing.decorators.get_session', side_effect=Exception("DB Down!")):
        output = retrieve_documents(prompt_template="Test DB Down", model_config={
                                    "model_name": "gemini-2.5-flash"})

    elapsed = time.perf_counter() - start

    assert output is not None
    assert elapsed < 0.5  # Non-blocking, fast


@patch('app.client.genai.Client')
@patch('monitoring.tracing.decorators.enqueue_trace')
def test_multistep_span_hierarchy(mock_enqueue, mock_client_cls):
    """
    Verify that nested calls correctly assign the parent_span_id to children.
    """
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.text = "Output"
    mock_response.usage_metadata = MagicMock(prompt_token_count=10, candidates_token_count=5)
    mock_client.models.generate_content.return_value = mock_response

    generate_credit_memo(prompt_template="Outer", model_config={
                         "model_name": "gemini-2.5-flash"})

    assert mock_enqueue.call_count == 4

    traces = [call.args[0] for call in mock_enqueue.call_args_list]

    # The order of completion (and thus enqueueing) is inner first, then outer.
    t_retrieve = traces[0]
    t_draft = traces[1]
    t_check = traces[2]
    t_outer = traces[3]

    assert t_retrieve["feature_name"] == "credit_memo_drafting"
    assert t_retrieve["parent_span_id"] == t_outer["id"]
    assert t_draft["parent_span_id"] == t_outer["id"]
    assert t_check["parent_span_id"] == t_outer["id"]
    assert t_outer["parent_span_id"] is None


def test_async_writer_resilience():
    """
    Test that if the DB is down, the async writer puts the trace back into the queue
    to retry later.
    """
    from monitoring.tracing.async_writer import worker, trace_queue
    import uuid

    trace_data = {
        "id": uuid.uuid4(),
        "trace_type": "feature",
        "feature_name": "resilience_test",
        "prompt_version_id": uuid.uuid4(),
        "model_config_id": uuid.uuid4(),
        "input_payload": {"test": 1},
    }
    
    trace_queue.put(None)  # Stop the background worker first
    import threading
    for t in threading.enumerate():
        if t.name == "writer_thread":
            t.join(timeout=1.0)
            
    # Clear the queue just in case
    while not trace_queue.empty():
        trace_queue.get()
        
    trace_queue.put(trace_data)
    trace_queue.put(None)  # Sentinel to stop our synchronous worker
    # We will verify that trace_data is back in the queue.
    with patch('monitoring.tracing.async_writer.get_session', side_effect=Exception("DB Down!")):
        # We also need to patch time.sleep so it doesn't wait 1s during the test
        with patch('time.sleep', return_value=None):
            worker()
            
    # Worker stopped because of None. Let's see what's left in the queue.
    # The trace_data should have been re-enqueued.
    # Actually, the worker might process the re-enqueued trace_data before it processes None
    # if it puts trace_data back, then gets the next item (which is None).
    assert not trace_queue.empty()
    item = trace_queue.get()
    assert item["feature_name"] == "resilience_test"
