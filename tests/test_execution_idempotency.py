import pytest

from exchanges.execution_idempotency import (
    ExecutionIdempotencyGuard,
)


@pytest.fixture
def guard():
    return ExecutionIdempotencyGuard()


def test_first_request_is_accepted(guard):
    result = guard.register("exec-001")

    assert result["accepted"] is True
    assert result["duplicate"] is False


def test_duplicate_request_is_rejected(guard):
    guard.register("exec-001")

    result = guard.register("exec-001")

    assert result["accepted"] is False
    assert result["duplicate"] is True
    assert result["reason"] == "DUPLICATE_EXECUTION"


def test_different_execution_ids_are_independent(guard):
    first = guard.register("exec-001")
    second = guard.register("exec-002")

    assert first["accepted"] is True
    assert second["accepted"] is True


def test_empty_execution_id_is_rejected(guard):
    with pytest.raises(ValueError, match="execution_id is required"):
        guard.register("")


def test_none_execution_id_is_rejected(guard):
    with pytest.raises(ValueError, match="execution_id is required"):
        guard.register(None)


def test_release_allows_future_retry(guard):
    guard.register("exec-001")

    assert guard.release("exec-001") is True

    result = guard.register("exec-001")
    assert result["accepted"] is True


def test_release_unknown_execution_returns_false(guard):
    assert guard.release("missing") is False


def test_contains_reports_registered_state(guard):
    guard.register("exec-001")

    assert guard.contains("exec-001") is True
    assert guard.contains("exec-002") is False


def test_clear_removes_all_registered_executions(guard):
    guard.register("exec-001")
    guard.register("exec-002")

    guard.clear()

    assert guard.contains("exec-001") is False
    assert guard.contains("exec-002") is False


def test_whitespace_ids_are_normalized(guard):
    guard.register("  exec-001  ")

    result = guard.register("exec-001")

    assert result["duplicate"] is True
