import pytest

from core.staged_test_trade_execution_permission import (
    StagedTestTradeExecutionPermission,
)


def ready_handoff():
    return {
        "handoff_ready": True,
        "reason": "approved_test_trade_ready",
        "route_id": "DIRECT-ETH",
        "route_type": "direct_cross_exchange",
        "approval_id": "ARB-001",
        "asset": "ETH",
        "trade_amount": 250.0,
        "live_order_submitted": False,
    }


def test_permission_defaults_to_not_granted():
    gate = StagedTestTradeExecutionPermission()

    result = gate.create(
        handoff_result=ready_handoff(),
    )

    assert result["permission_granted"] is False
    assert result["status"] == "awaiting_execution_permission"
    assert result["live_order_submitted"] is False


def test_explicit_permission_can_be_granted():
    gate = StagedTestTradeExecutionPermission()

    request = gate.create(
        handoff_result=ready_handoff(),
    )

    result = gate.grant(
        permission_id=request["permission_id"],
        trade_amount=250.0,
    )

    assert result["permission_granted"] is True
    assert result["status"] == "execution_permission_granted"
    assert result["trade_amount"] == 250.0
    assert result["live_order_submitted"] is False


def test_permission_requires_matching_trade_amount():
    gate = StagedTestTradeExecutionPermission()

    request = gate.create(
        handoff_result=ready_handoff(),
    )

    result = gate.grant(
        permission_id=request["permission_id"],
        trade_amount=100.0,
    )

    assert result["permission_granted"] is False
    assert result["reason"] == "trade_amount_mismatch"
    assert result["live_order_submitted"] is False


def test_non_ready_handoff_cannot_create_permission():
    gate = StagedTestTradeExecutionPermission()

    handoff = ready_handoff()
    handoff["handoff_ready"] = False

    result = gate.create(
        handoff_result=handoff,
    )

    assert result["permission_granted"] is False
    assert result["status"] == "blocked"
    assert result["reason"] == "handoff_not_ready"


def test_existing_live_order_blocks_permission():
    gate = StagedTestTradeExecutionPermission()

    handoff = ready_handoff()
    handoff["live_order_submitted"] = True

    result = gate.create(
        handoff_result=handoff,
    )

    assert result["permission_granted"] is False
    assert result["reason"] == "live_order_already_submitted"


def test_unknown_permission_id_cannot_be_granted():
    gate = StagedTestTradeExecutionPermission()

    result = gate.grant(
        permission_id="UNKNOWN",
        trade_amount=250.0,
    )

    assert result["permission_granted"] is False
    assert result["status"] == "not_found"
    assert result["live_order_submitted"] is False


def test_permission_is_single_use():
    gate = StagedTestTradeExecutionPermission()

    request = gate.create(
        handoff_result=ready_handoff(),
    )

    first = gate.grant(
        permission_id=request["permission_id"],
        trade_amount=250.0,
    )

    second = gate.grant(
        permission_id=request["permission_id"],
        trade_amount=250.0,
    )

    assert first["permission_granted"] is True
    assert second["permission_granted"] is False
    assert second["status"] == "not_found"


def test_missing_handoff_is_rejected():
    gate = StagedTestTradeExecutionPermission()

    with pytest.raises(
        ValueError,
        match="handoff_result is required",
    ):
        gate.create(
            handoff_result=None,
        )
