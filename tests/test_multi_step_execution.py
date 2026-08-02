import pytest

from exchanges.multi_step_execution import MultiStepExecution


def test_create_workflow():
    workflow = MultiStepExecution(
        execution_id="ARB-001",
        steps=["BUY", "TRANSFER", "SELL"],
    )

    assert workflow is not None


def test_initial_step_state():
    workflow = MultiStepExecution(
        execution_id="ARB-002",
        steps=["BUY", "TRANSFER", "SELL"],
    )

    assert workflow.get_current_step() == "BUY"


def test_complete_first_step():
    workflow = MultiStepExecution(
        execution_id="ARB-003",
        steps=["BUY", "TRANSFER", "SELL"],
    )

    result = workflow.complete_step()

    assert result["step"] == "BUY"
    assert result["status"] == "completed"


def test_move_through_workflow():
    workflow = MultiStepExecution(
        execution_id="ARB-004",
        steps=["BUY", "TRANSFER", "SELL"],
    )

    workflow.complete_step()
    workflow.complete_step()

    assert workflow.get_current_step() == "SELL"


def test_complete_full_execution():
    workflow = MultiStepExecution(
        execution_id="ARB-005",
        steps=["BUY", "TRANSFER", "SELL"],
    )

    workflow.complete_step()
    workflow.complete_step()
    result = workflow.complete_step()

    assert result["status"] == "workflow_completed"


def test_fail_step():
    workflow = MultiStepExecution(
        execution_id="ARB-006",
        steps=["BUY", "TRANSFER", "SELL"],
    )

    result = workflow.fail_step("network_error")

    assert result["status"] == "failed"
    assert result["reason"] == "network_error"


def test_resume_failed_step():
    workflow = MultiStepExecution(
        execution_id="ARB-007",
        steps=["BUY", "TRANSFER", "SELL"],
    )

    workflow.complete_step()
    workflow.fail_step("transfer_failed")

    result = workflow.resume()

    assert result["step"] == "TRANSFER"


def test_execution_history_recorded():
    workflow = MultiStepExecution(
        execution_id="ARB-008",
        steps=["BUY", "TRANSFER", "SELL"],
    )

    workflow.complete_step()

    history = workflow.get_history()

    assert len(history) == 2
