import pytest

from exchanges.execution_control_pipeline import ExecutionControlPipeline


def valid_context():
    return {
        "exchange_healthy": True,
        "market_data_fresh": True,
        "sufficient_balance": True,
        "valid_order_size": True,
        "network_supported": True,
        "reconciliation_clear": True,
    }


@pytest.fixture
def pipeline():
    return ExecutionControlPipeline()


def test_safe_valid_transition_is_allowed(pipeline):
    result = pipeline.evaluate(
        execution_id="EXEC-001",
        context=valid_context(),
        current_state="CREATED",
        target_state="VALIDATED",
    )

    assert result["allowed"] is True
    assert result["decision"] == "EXECUTION_ALLOWED"


def test_failed_safety_gate_blocks_execution(pipeline):
    context = valid_context()
    context["exchange_healthy"] = False

    result = pipeline.evaluate(
        execution_id="EXEC-001",
        context=context,
        current_state="CREATED",
        target_state="VALIDATED",
    )

    assert result["allowed"] is False
    assert result["decision"] == "SAFETY_BLOCKED"
    assert "EXCHANGE_UNHEALTHY" in result["reasons"]


def test_invalid_transition_blocks_execution(pipeline):
    result = pipeline.evaluate(
        execution_id="EXEC-001",
        context=valid_context(),
        current_state="CREATED",
        target_state="COMPLETED",
    )

    assert result["allowed"] is False
    assert result["decision"] == "TRANSITION_BLOCKED"
    assert result["reasons"] == ["INVALID_STATE_TRANSITION"]


def test_safety_check_has_priority_over_transition(pipeline):
    context = valid_context()
    context["market_data_fresh"] = False

    result = pipeline.evaluate(
        execution_id="EXEC-001",
        context=context,
        current_state="CREATED",
        target_state="COMPLETED",
    )

    assert result["decision"] == "SAFETY_BLOCKED"


def test_allowed_decision_is_written_to_audit_history(pipeline):
    pipeline.evaluate(
        execution_id="EXEC-001",
        context=valid_context(),
        current_state="CREATED",
        target_state="VALIDATED",
    )

    history = pipeline.audit_history("EXEC-001")

    assert len(history) == 1
    assert history[0]["event"] == "EXECUTION_ALLOWED"


def test_blocked_decision_is_written_to_audit_history(pipeline):
    context = valid_context()
    context["sufficient_balance"] = False

    pipeline.evaluate(
        execution_id="EXEC-001",
        context=context,
        current_state="CREATED",
        target_state="VALIDATED",
    )

    latest = pipeline.latest_audit("EXEC-001")

    assert latest["event"] == "SAFETY_BLOCKED"
    assert "INSUFFICIENT_BALANCE" in latest["metadata"]["reasons"]


def test_missing_execution_id_is_rejected(pipeline):
    with pytest.raises(ValueError, match="execution_id is required"):
        pipeline.evaluate(
            execution_id="",
            context=valid_context(),
            current_state="CREATED",
            target_state="VALIDATED",
        )


def test_none_context_is_rejected(pipeline):
    with pytest.raises(ValueError, match="context is required"):
        pipeline.evaluate(
            execution_id="EXEC-001",
            context=None,
            current_state="CREATED",
            target_state="VALIDATED",
        )
