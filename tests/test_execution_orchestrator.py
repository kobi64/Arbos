import pytest

from exchanges.execution_orchestrator import ExecutionOrchestrator


def test_create_orchestrator():
    orchestrator = ExecutionOrchestrator()

    assert orchestrator is not None


def test_execute_approved_trade():
    orchestrator = ExecutionOrchestrator()

    result = orchestrator.execute(
        trade_id="TRADE-001",
        risk_status="approved",
    )

    assert result["status"] == "completed"
    assert result["trade_id"] == "TRADE-001"


def test_reject_trade_failed_risk_check():
    orchestrator = ExecutionOrchestrator()

    result = orchestrator.execute(
        trade_id="TRADE-002",
        risk_status="rejected",
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "risk_check_failed"


def test_missing_trade_id_rejected():
    orchestrator = ExecutionOrchestrator()

    with pytest.raises(ValueError):
        orchestrator.execute(
            trade_id="",
            risk_status="approved",
        )


def test_execution_history_recorded():
    orchestrator = ExecutionOrchestrator()

    orchestrator.execute(
        trade_id="TRADE-003",
        risk_status="approved",
    )

    history = orchestrator.get_history()

    assert isinstance(history, list)
    assert len(history) == 1


def test_multiple_executions_tracked():
    orchestrator = ExecutionOrchestrator()

    orchestrator.execute(
        trade_id="TRADE-004",
        risk_status="approved",
    )

    orchestrator.execute(
        trade_id="TRADE-005",
        risk_status="approved",
    )

    history = orchestrator.get_history()

    assert len(history) == 2


def test_invalid_risk_state_rejected():
    orchestrator = ExecutionOrchestrator()

    with pytest.raises(ValueError):
        orchestrator.execute(
            trade_id="TRADE-006",
            risk_status="unknown",
        )


def test_failed_execution_recorded():
    orchestrator = ExecutionOrchestrator()

    result = orchestrator.execute(
        trade_id="TRADE-007",
        risk_status="approved",
        execution_result="failed",
    )

    assert result["status"] == "failed"
