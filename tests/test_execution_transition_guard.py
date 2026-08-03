import pytest

from exchanges.execution_transition_guard import (
    ExecutionTransitionGuard,
)


@pytest.fixture
def guard():
    return ExecutionTransitionGuard()


def test_created_can_move_to_validated(guard):
    result = guard.evaluate("CREATED", "VALIDATED")

    assert result["allowed"] is True
    assert result["reason"] is None


def test_validated_can_move_to_approved(guard):
    result = guard.evaluate("VALIDATED", "APPROVED")

    assert result["allowed"] is True


def test_approved_can_move_to_executing(guard):
    result = guard.evaluate("APPROVED", "EXECUTING")

    assert result["allowed"] is True


def test_executing_can_move_to_completed(guard):
    result = guard.evaluate("EXECUTING", "COMPLETED")

    assert result["allowed"] is True


def test_executing_can_move_to_failed(guard):
    result = guard.evaluate("EXECUTING", "FAILED")

    assert result["allowed"] is True


def test_failed_can_move_to_recovery(guard):
    result = guard.evaluate("FAILED", "RECOVERY")

    assert result["allowed"] is True


def test_invalid_jump_is_blocked(guard):
    result = guard.evaluate("CREATED", "COMPLETED")

    assert result["allowed"] is False
    assert result["reason"] == "INVALID_STATE_TRANSITION"


def test_closed_is_terminal(guard):
    result = guard.evaluate("CLOSED", "EXECUTING")

    assert result["allowed"] is False
    assert result["reason"] == "TERMINAL_STATE"


def test_unknown_current_state_is_rejected(guard):
    with pytest.raises(ValueError, match="unsupported current_state"):
        guard.evaluate("BANANA", "CREATED")


def test_unknown_target_state_is_rejected(guard):
    with pytest.raises(ValueError, match="unsupported target_state"):
        guard.evaluate("CREATED", "BANANA")


def test_states_are_case_insensitive(guard):
    result = guard.evaluate("created", "validated")

    assert result["allowed"] is True
    assert result["current_state"] == "CREATED"
    assert result["target_state"] == "VALIDATED"


def test_guard_matches_ex031_transition_rules(guard):
    assert guard.evaluate("RECOVERY", "EXECUTING")["allowed"] is True
    assert guard.evaluate("COMPLETED", "CLOSED")["allowed"] is True
