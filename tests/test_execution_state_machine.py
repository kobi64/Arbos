import pytest

from exchanges.execution_state_machine import ExecutionStateMachine


def test_create_state_machine():
    machine = ExecutionStateMachine()

    assert machine is not None


def test_initial_state_is_created():
    machine = ExecutionStateMachine(
        execution_id="EXEC-001"
    )

    assert machine.get_state() == "CREATED"


def test_valid_transition_created_to_validated():
    machine = ExecutionStateMachine(
        execution_id="EXEC-002"
    )

    result = machine.transition("VALIDATED")

    assert result["state"] == "VALIDATED"


def test_valid_execution_flow():
    machine = ExecutionStateMachine(
        execution_id="EXEC-003"
    )

    machine.transition("VALIDATED")
    machine.transition("APPROVED")
    machine.transition("EXECUTING")
    result = machine.transition("COMPLETED")

    assert result["state"] == "COMPLETED"


def test_invalid_transition_rejected():
    machine = ExecutionStateMachine(
        execution_id="EXEC-004"
    )

    with pytest.raises(ValueError):
        machine.transition("COMPLETED")


def test_failed_execution_path():
    machine = ExecutionStateMachine(
        execution_id="EXEC-005"
    )

    machine.transition("VALIDATED")
    machine.transition("APPROVED")
    machine.transition("EXECUTING")

    result = machine.transition("FAILED")

    assert result["state"] == "FAILED"


def test_recovery_transition():
    machine = ExecutionStateMachine(
        execution_id="EXEC-006"
    )

    machine.transition("VALIDATED")
    machine.transition("APPROVED")
    machine.transition("EXECUTING")
    machine.transition("FAILED")

    result = machine.transition("RECOVERY")

    assert result["state"] == "RECOVERY"


def test_transition_history_recorded():
    machine = ExecutionStateMachine(
        execution_id="EXEC-007"
    )

    machine.transition("VALIDATED")
    machine.transition("APPROVED")

    history = machine.get_history()

    assert len(history) == 3
