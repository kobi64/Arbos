import pytest

from core.controlled_test_trade_execution_adapter import (
    ControlledTestTradeExecutionAdapter,
)


def granted_permission():
    return {
        "permission_id": "PERM-001",
        "permission_granted": True,
        "status": "execution_permission_granted",
        "route_id": "DIRECT-ETH",
        "approval_id": "ARB-001",
        "asset": "ETH",
        "buy_exchange": "kucoin",
        "sell_exchange": "gate",
        "trade_amount": 250.0,
        "live_order_submitted": False,
    }


def test_granted_permission_is_authorised_by_controlled_manager():
    adapter = ControlledTestTradeExecutionAdapter(
        max_trade_size=300.0
    )

    result = adapter.authorise(
        permission_result=granted_permission(),
    )

    assert result["authorised"] is True
    assert result["reason"] == "execution_authorised"
    assert result["trade_amount"] == 250.0
    assert result["permission_id"] == "PERM-001"
    assert result["live_order_submitted"] is False


def test_ungranted_permission_is_blocked():
    adapter = ControlledTestTradeExecutionAdapter()

    permission = granted_permission()
    permission["permission_granted"] = False
    permission["status"] = "awaiting_execution_permission"

    result = adapter.authorise(
        permission_result=permission,
    )

    assert result["authorised"] is False
    assert result["reason"] == "execution_permission_required"
    assert result["live_order_submitted"] is False


def test_oversized_trade_is_blocked():
    adapter = ControlledTestTradeExecutionAdapter(
        max_trade_size=100.0
    )

    result = adapter.authorise(
        permission_result=granted_permission(),
    )

    assert result["authorised"] is False
    assert result["reason"] == "trade_size_limit_exceeded"
    assert result["live_order_submitted"] is False


def test_existing_live_order_is_blocked():
    adapter = ControlledTestTradeExecutionAdapter()

    permission = granted_permission()
    permission["live_order_submitted"] = True

    result = adapter.authorise(
        permission_result=permission,
    )

    assert result["authorised"] is False
    assert result["reason"] == "live_order_already_submitted"
    assert result["live_order_submitted"] is True


def test_adapter_authorisation_is_single_use():
    adapter = ControlledTestTradeExecutionAdapter()

    permission = granted_permission()

    first = adapter.authorise(
        permission_result=permission,
    )

    second = adapter.authorise(
        permission_result=permission,
    )

    assert first["authorised"] is True
    assert second["authorised"] is False
    assert second["reason"] == "duplicate_execution_blocked"
    assert second["live_order_submitted"] is False


def test_missing_permission_result_is_rejected():
    adapter = ControlledTestTradeExecutionAdapter()

    with pytest.raises(
        ValueError,
        match="permission_result is required",
    ):
        adapter.authorise(
            permission_result=None,
        )


# EX-330 — execution destination propagation audit


def test_authorised_execution_preserves_approved_exchange_identity():
    adapter = ControlledTestTradeExecutionAdapter(
        max_trade_size=300.0
    )

    permission = granted_permission()
    permission["buy_exchange"] = "kucoin"
    permission["sell_exchange"] = "gate"

    result = adapter.authorise(
        permission_result=permission,
    )

    assert result["authorised"] is True
    assert result["buy_exchange"] == "kucoin"
    assert result["sell_exchange"] == "gate"


@pytest.mark.parametrize(
    "field,value",
    [
        ("buy_exchange", None),
        ("buy_exchange", ""),
        ("buy_exchange", "   "),
        ("buy_exchange", 0),
        ("buy_exchange", False),
        ("sell_exchange", None),
        ("sell_exchange", ""),
        ("sell_exchange", "   "),
        ("sell_exchange", 0),
        ("sell_exchange", False),
    ],
)
def test_authorisation_requires_approved_exchange_identity(
    field,
    value,
):
    adapter = ControlledTestTradeExecutionAdapter(
        max_trade_size=300.0
    )

    permission = granted_permission()
    permission["buy_exchange"] = "kucoin"
    permission["sell_exchange"] = "gate"
    permission[field] = value

    result = adapter.authorise(
        permission_result=permission,
    )

    assert result["authorised"] is False
    assert result["reason"] == f"{field}_required"
    assert result["live_order_submitted"] is False


def test_authorised_exchange_identity_is_normalized():
    adapter = ControlledTestTradeExecutionAdapter(
        max_trade_size=300.0
    )

    permission = granted_permission()
    permission["buy_exchange"] = "  kucoin  "
    permission["sell_exchange"] = "  gate  "

    result = adapter.authorise(
        permission_result=permission,
    )

    assert result["authorised"] is True
    assert result["buy_exchange"] == "kucoin"
    assert result["sell_exchange"] == "gate"


def test_authorised_execution_destination_flows_into_buy_intent():
    adapter = ControlledTestTradeExecutionAdapter(
        max_trade_size=300.0
    )

    permission = granted_permission()
    permission["buy_exchange"] = "kucoin"
    permission["sell_exchange"] = "gate"

    execution = adapter.authorise(
        permission_result=permission,
    )

    from core.controlled_test_trade_order_intent import (
        ControlledTestTradeOrderIntent,
    )

    intent = ControlledTestTradeOrderIntent().build(
        execution_result=execution,
        exchange="kucoin",
        symbol="ETH/USDT",
        side="buy",
    )

    assert intent["intent_ready"] is True
    assert intent["exchange"] == "kucoin"


def test_authorised_execution_cannot_redirect_buy_destination():
    adapter = ControlledTestTradeExecutionAdapter(
        max_trade_size=300.0
    )

    permission = granted_permission()
    permission["buy_exchange"] = "kucoin"
    permission["sell_exchange"] = "gate"

    execution = adapter.authorise(
        permission_result=permission,
    )

    from core.controlled_test_trade_order_intent import (
        ControlledTestTradeOrderIntent,
    )

    intent = ControlledTestTradeOrderIntent().build(
        execution_result=execution,
        exchange="gate",
        symbol="ETH/USDT",
        side="buy",
    )

    assert intent["intent_ready"] is False
    assert intent["reason"] == "buy_exchange_mismatch"
    assert intent["live_order_submitted"] is False
