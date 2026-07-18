import time
from unittest.mock import patch
from app.feature.credit_memo import retrieve_documents, generate_credit_memo


def test_kill_the_db_resilience():
    """
    If the DB connection fails during resolving foreign keys,
    the decorator should still return the output quickly without throwing to the user.
    """
    start = time.perf_counter()
    # Mocking the session resolver to simulate a DB failure
    with patch('monitoring.tracing.decorators.get_session', side_effect=Exception("DB Down!")):
        output = retrieve_documents(prompt_template="Test DB Down", model_config={
                                    "model_name": "gpt-4o-2026-03-01"})

    elapsed = time.perf_counter() - start

    assert output is not None
    assert elapsed < 0.5  # Non-blocking, fast


@patch('monitoring.tracing.decorators.enqueue_trace')
def test_multistep_span_hierarchy(mock_enqueue):
    """
    Verify that nested calls correctly assign the parent_span_id to children.
    """
    generate_credit_memo(prompt_template="Outer", model_config={
                         "model_name": "gpt-4o-2026-03-01"})

    assert mock_enqueue.call_count == 3

    traces = [call.args[0] for call in mock_enqueue.call_args_list]

    # The order of completion (and thus enqueueing) is inner first, then outer.
    t_retrieve = traces[0]
    t_check = traces[1]
    t_outer = traces[2]

    assert t_retrieve["feature_name"] == "credit_memo_drafting"
    assert t_retrieve["parent_span_id"] == t_outer["id"]
    assert t_check["parent_span_id"] == t_outer["id"]
    assert t_outer["parent_span_id"] is None
