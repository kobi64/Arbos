import pytest

from exchanges.execution_recovery_decision import (
    ExecutionRecoveryDecisionEngine,
)


@pytest.fixture
def engine():
    return ExecutionRecoveryDecisionEngine()


def test_retryable_failure_retries(engine):
    result = engine.decide(
        execution_state="FAILED",
        retry_allowed=True,
        reconciliation_required=False,
        cancel_possible=False,
    )

    assert result["action"] == "RETRY"
    assert result["escalate"] is False


def test_reconciliation_has_priority(engine):
    result = engine.decide(
        execution_state="FAILED",
        retry_allowed=True,
        reconciliation_required=True,
        cancel_possible=True,
    )

    assert result["action"] == "RECONCILE"
    assert result["escalate"] is False


def test_uncertain_state_requires_reconciliation(engine):
    result = engine.decide(
        execution_state="UNKNOWN",
        retry_allowed=False,
        reconciliation_required=False,
        cancel_possible=True,
    )

    assert result["action"] == "RECONCILE"
    assert result["escalate"] is True


def test_cancel_when_retry_not_allowed(engine):
    result = engine.decide(
        execution_state="FAILED",
        retry_allowed=False,
        reconciliation_required=False,
        cancel_possible=True,
    )

    assert result["action"] == "CANCEL"
    assert result["escalate"] is False


def test_escalate_when_no_safe_recovery_exists(engine):
    result = engine.decide(
        execution_state="FAILED",
        retry_allowed=False,
        reconciliation_required=False,
        cancel_possible=False,
    )

    assert result["action"] == "ESCALATE"
    assert result["escalate"] is True


def test_completed_execution_stops(engine):
    result = engine.decide(
        execution_state="COMPLETED",
        retry_allowed=True,
        reconciliation_required=True,
        cancel_possible=True,
    )

    assert result["action"] == "STOP"
    assert result["escalate"] is False


def test_closed_execution_stops(engine):
    result = engine.decide(
        execution_state="CLOSED",
        retry_allowed=False,
        reconciliation_required=False,
        cancel_possible=False,
    )

    assert result["action"] == "STOP"


def test_recovery_state_continues_recovery(engine):
    result = engine.decide(
        execution_state="RECOVERY",
        retry_allowed=False,
        reconciliation_required=False,
        cancel_possible=False,
    )

    assert result["action"] == "CONTINUE_RECOVERY"


def test_unknown_execution_state_is_rejected(engine):
    with pytest.raises(ValueError, match="unsupported execution_state"):
        engine.decide(
            execution_state="BANANA",
            retry_allowed=False,
            reconciliation_required=False,
            cancel_possible=False,
        )


def test_states_are_case_insensitive(engine):
    result = engine.decide(
        execution_state="failed",
        retry_allowed=True,
        reconciliation_required=False,
        cancel_possible=False,
    )

    assert result["action"] == "RETRY"
