"""Offline tests for the supervisor's retry policy."""
from langgraph.graph import END
from agents.supervisor import parse_quality_score, should_retry, MAX_ITERATIONS


def test_parse_valid_integer_score():
    assert parse_quality_score('{"score": 3, "reason": "limited coverage"}') == 3


def test_reject_invalid_quality_scores():
    for value in ('{"score": "3"}', '{"score": 11}', '{"score": true}', 'not json'):
        assert parse_quality_score(value) is None


def test_retry_is_based_on_structured_score():
    assert should_retry({"quality_score": 3, "iteration": 1}) == "researcher"
    assert should_retry({"quality_score": 4, "iteration": 1}) == END
    assert should_retry({"quality_score": 10, "iteration": 1}) == END
    assert should_retry({"quality_score": 3, "iteration": MAX_ITERATIONS}) == END
    assert should_retry({"quality_score": None, "iteration": 1}) == END


def test_score_ten_is_not_mistaken_for_score_one():
    state = {"quality_score": 10, "iteration": 1, "status_log": ["Supervisor: score 10/10"]}
    assert should_retry(state) == END
