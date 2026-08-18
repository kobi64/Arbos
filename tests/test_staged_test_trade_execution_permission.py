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
        "buy_exchange": "kucoin",
        "sell_exchange": "gate",
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


@pytest.mark.parametrize(
    "trade_amount",
    [
        None,
        "bad",
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        0.0,
        -1.0,
    ],
)
def test_create_rejects_invalid_trade_amount(
    trade_amount,
):
    gate = StagedTestTradeExecutionPermission()

    handoff = ready_handoff()
    handoff["trade_amount"] = trade_amount

    result = gate.create(
        handoff_result=handoff,
    )

    assert result["permission_granted"] is False
    assert result["status"] == "blocked"
    assert result["reason"] == "invalid_trade_amount"


def test_create_supports_numeric_string_amount():
    gate = StagedTestTradeExecutionPermission()

    handoff = ready_handoff()
    handoff["trade_amount"] = "250"

    result = gate.create(
        handoff_result=handoff,
    )

    assert result["status"] == "awaiting_execution_permission"
    assert result["trade_amount"] == 250.0


@pytest.mark.parametrize(
    "trade_amount",
    [
        None,
        "bad",
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        0.0,
        -1.0,
    ],
)
def test_grant_rejects_invalid_supplied_amount(
    trade_amount,
):
    gate = StagedTestTradeExecutionPermission()

    request = gate.create(
        handoff_result=ready_handoff(),
    )

    result = gate.grant(
        permission_id=request["permission_id"],
        trade_amount=trade_amount,
    )

    assert result["permission_granted"] is False
    assert result["status"] == "blocked"
    assert result["reason"] == "invalid_trade_amount"


def test_invalid_grant_does_not_consume_permission():
    gate = StagedTestTradeExecutionPermission()

    request = gate.create(
        handoff_result=ready_handoff(),
    )

    blocked = gate.grant(
        permission_id=request["permission_id"],
        trade_amount=float("nan"),
    )

    granted = gate.grant(
        permission_id=request["permission_id"],
        trade_amount=250.0,
    )

    assert blocked["permission_granted"] is False
    assert granted["permission_granted"] is True


def test_numeric_string_grant_amount_remains_supported():
    gate = StagedTestTradeExecutionPermission()

    request = gate.create(
        handoff_result=ready_handoff(),
    )

    result = gate.grant(
        permission_id=request["permission_id"],
        trade_amount="250",
    )

    assert result["permission_granted"] is True
    assert result["trade_amount"] == 250.0


@pytest.mark.parametrize(
    "field,value",
    [
        ("route_id", None),
        ("route_id", ""),
        ("route_id", "   "),
        ("route_id", 0),
        ("route_id", False),
        ("approval_id", None),
        ("approval_id", ""),
        ("approval_id", "   "),
        ("approval_id", 0),
        ("approval_id", False),
        ("asset", None),
        ("asset", ""),
        ("asset", "   "),
        ("asset", 0),
        ("asset", False),
    ],
)
def test_create_requires_bound_execution_identity(
    field,
    value,
):
    gate = StagedTestTradeExecutionPermission()

    handoff = ready_handoff()
    handoff[field] = value

    result = gate.create(
        handoff_result=handoff,
    )

    assert result["permission_granted"] is False
    assert result["status"] == "blocked"
    assert result["reason"] == f"{field}_required"


def test_identity_strings_are_normalized_on_permission_create():
    gate = StagedTestTradeExecutionPermission()

    handoff = ready_handoff()
    handoff["route_id"] = "  DIRECT-ETH  "
    handoff["approval_id"] = "  ARB-001  "
    handoff["asset"] = " eth "

    result = gate.create(
        handoff_result=handoff,
    )

    assert result["route_id"] == "DIRECT-ETH"
    assert result["approval_id"] == "ARB-001"
    assert result["asset"] == "ETH"


def test_permission_request_preserves_exchange_identity():
    gate = StagedTestTradeExecutionPermission()

    result = gate.create(
        handoff_result=ready_handoff(),
    )

    assert result["buy_exchange"] == "kucoin"
    assert result["sell_exchange"] == "gate"


def test_granted_permission_preserves_exchange_identity():
    gate = StagedTestTradeExecutionPermission()

    request = gate.create(
        handoff_result=ready_handoff(),
    )

    result = gate.grant(
        permission_id=request["permission_id"],
        trade_amount=250.0,
    )

    assert result["permission_granted"] is True
    assert result["buy_exchange"] == "kucoin"
    assert result["sell_exchange"] == "gate"
