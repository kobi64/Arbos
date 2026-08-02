import pytest

from exchanges.execution_engine import ExecutionEngine


def test_execution_request_requires_approval():
    result = ExecutionEngine.create_request(
        approval_status="awaiting_approval",
        asset="BTC",
        amount=1000.0,
        route="ExchangeA -> ExchangeB",
    )

    assert result["status"] == "blocked"
    assert result["reason"] == "approval_required"


def test_execution_request_created_after_approval():
    result = ExecutionEngine.create_request(
        approval_status="approved",
        asset="BTC",
        amount=1000.0,
        route="ExchangeA -> ExchangeB",
    )

    assert result["status"] == "created"
    assert result["execution_state"] == "CREATED"


def test_execution_can_start_when_created():
    result = ExecutionEngine.start_execution(
        execution_id="EXEC-001"
    )

    assert result["status"] == "executing"
    assert result["execution_state"] == "EXECUTING"


def test_execution_completion():
    result = ExecutionEngine.complete_execution(
        execution_id="EXEC-002"
    )

    assert result["status"] == "completed"
    assert result["execution_state"] == "COMPLETED"


def test_execution_failure_tracking():
    result = ExecutionEngine.fail_execution(
        execution_id="EXEC-003",
        reason="exchange_timeout",
    )

    assert result["status"] == "failed"
    assert result["execution_state"] == "FAILED"
    assert result["reason"] == "exchange_timeout"


def test_execution_cancellation():
    result = ExecutionEngine.cancel_execution(
        execution_id="EXEC-004",
        reason="user_cancelled",
    )

    assert result["status"] == "cancelled"
    assert result["execution_state"] == "CANCELLED"


def test_invalid_execution_amount_rejected():
    with pytest.raises(ValueError):
        ExecutionEngine.create_request(
            approval_status="approved",
            asset="BTC",
            amount=0,
            route="ExchangeA -> ExchangeB",
        )


def test_missing_asset_rejected():
    with pytest.raises(ValueError):
        ExecutionEngine.create_request(
            approval_status="approved",
            asset="",
            amount=1000.0,
            route="ExchangeA -> ExchangeB",
        )
