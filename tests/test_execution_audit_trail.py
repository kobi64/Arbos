import pytest

from exchanges.execution_audit_trail import (
    ExecutionAuditTrail,
)


@pytest.fixture
def audit():
    return ExecutionAuditTrail()


def test_first_event_is_recorded(audit):
    audit.record(
        execution_id="EX001",
        event="EXECUTION_STARTED",
        state="CREATED",
    )

    history = audit.history("EX001")

    assert len(history) == 1
    assert history[0]["event"] == "EXECUTION_STARTED"


def test_multiple_events_preserve_order(audit):
    audit.record("EX001", "START", "CREATED")
    audit.record("EX001", "VALIDATED", "VALIDATED")
    audit.record("EX001", "EXECUTING", "EXECUTING")

    history = audit.history("EX001")

    assert [e["event"] for e in history] == [
        "START",
        "VALIDATED",
        "EXECUTING",
    ]


def test_separate_executions_are_isolated(audit):
    audit.record("A", "START", "CREATED")
    audit.record("B", "START", "CREATED")

    assert len(audit.history("A")) == 1
    assert len(audit.history("B")) == 1


def test_latest_event_returns_last_record(audit):
    audit.record("EX001", "START", "CREATED")
    audit.record("EX001", "DONE", "COMPLETED")

    latest = audit.latest("EX001")

    assert latest["event"] == "DONE"
    assert latest["state"] == "COMPLETED"


def test_unknown_execution_returns_empty_history(audit):
    assert audit.history("UNKNOWN") == []


def test_latest_unknown_execution_returns_none(audit):
    assert audit.latest("UNKNOWN") is None


def test_timestamp_is_recorded(audit):
    audit.record("EX001", "START", "CREATED")

    record = audit.latest("EX001")

    assert "timestamp" in record


def test_invalid_execution_id_is_rejected(audit):
    with pytest.raises(ValueError):
        audit.record("", "START", "CREATED")


def test_invalid_event_is_rejected(audit):
    with pytest.raises(ValueError):
        audit.record("EX001", "", "CREATED")


def test_invalid_state_is_rejected(audit):
    with pytest.raises(ValueError):
        audit.record("EX001", "START", "")
