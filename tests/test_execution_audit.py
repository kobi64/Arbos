import pytest

from exchanges.execution_audit import ExecutionAudit


def test_create_audit_record():
    result = ExecutionAudit.create_record(
        execution_id="EXEC-001",
        asset="BTC",
        amount=1000.0,
        route="ExchangeA -> ExchangeB",
    )

    assert result["status"] == "recorded"
    assert result["execution_id"] == "EXEC-001"


def test_record_initial_state():
    result = ExecutionAudit.record_state(
        execution_id="EXEC-002",
        state="CREATED",
    )

    assert result["state"] == "CREATED"
    assert result["status"] == "recorded"


def test_record_execution_progression():
    ExecutionAudit.record_state(
        execution_id="EXEC-003",
        state="CREATED",
    )

    result = ExecutionAudit.record_state(
        execution_id="EXEC-003",
        state="EXECUTING",
    )

    assert result["state"] == "EXECUTING"


def test_record_completion():
    result = ExecutionAudit.record_completion(
        execution_id="EXEC-004",
        profit=25.50,
    )

    assert result["status"] == "completed"
    assert result["profit"] == 25.50


def test_record_failure():
    result = ExecutionAudit.record_failure(
        execution_id="EXEC-005",
        reason="exchange_timeout",
    )

    assert result["status"] == "failed"
    assert result["reason"] == "exchange_timeout"


def test_get_execution_history():
    ExecutionAudit.record_state(
        execution_id="EXEC-006",
        state="CREATED",
    )

    result = ExecutionAudit.get_history(
        execution_id="EXEC-006"
    )

    assert isinstance(result, list)
    assert len(result) >= 1


def test_invalid_execution_id_rejected():
    with pytest.raises(ValueError):
        ExecutionAudit.record_state(
            execution_id="",
            state="CREATED",
        )


def test_invalid_state_rejected():
    with pytest.raises(ValueError):
        ExecutionAudit.record_state(
            execution_id="EXEC-007",
            state="UNKNOWN",
        )


@pytest.mark.parametrize(
    "amount",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_create_record_rejects_invalid_numeric_amount(amount):
    with pytest.raises(
        ValueError,
        match="invalid amount",
    ):
        ExecutionAudit.create_record(
            execution_id="EXEC-NUMERIC",
            asset="BTC",
            amount=amount,
            route="ExchangeA -> ExchangeB",
        )


def test_create_record_rejects_boolean_amount():
    with pytest.raises(
        ValueError,
        match="invalid amount",
    ):
        ExecutionAudit.create_record(
            execution_id="EXEC-BOOL",
            asset="BTC",
            amount=True,
            route="ExchangeA -> ExchangeB",
        )
