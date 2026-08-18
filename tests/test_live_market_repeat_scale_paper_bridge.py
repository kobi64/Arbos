import pytest

from core.live_market_repeat_scale_paper_bridge import (
    LiveMarketRepeatScalePaperBridge,
)
from core.staged_test_trade_execution_permission import (
    StagedTestTradeExecutionPermission,
)


class FakeMarketDataProvider:
    def __init__(self, prices=None):
        self.prices = (
            prices
            if prices is not None
            else {
                "ETH/USDT": 3200.0,
            }
        )
        self.requested_symbols = []

    def get_price(self, symbol):
        self.requested_symbols.append(
            symbol
        )
        return self.prices.get(symbol)


def granted_permission(
    trade_amount=0.2,
    approval_id="ARB-002",
    permission_id="PERM-002",
):
    return {
        "permission_id": permission_id,
        "approval_id": approval_id,
        "permission_granted": True,
        "status": "execution_permission_granted",
        "trade_amount": trade_amount,
        "test_trade": True,
        "live_order_submitted": False,
    }


def valid_order(
    quantity=0.2,
):
    return {
        "symbol": "ETH/USDT",
        "side": "sell",
        "order_type": "market",
        "quantity": quantity,
    }


def bridge(
    provider=None,
):
    return LiveMarketRepeatScalePaperBridge(
        provider or FakeMarketDataProvider()
    )


def test_granted_permission_executes_paper_order():
    result = bridge().execute(
        permission_result=granted_permission(),
        order=valid_order(),
    )

    assert result["executed"] is True
    assert result["paper_only"] is True
    assert (
        result["reason"]
        == "live_market_repeat_scale_paper_executed"
    )


def test_live_market_price_is_used():
    result = bridge().execute(
        permission_result=granted_permission(),
        order=valid_order(),
    )

    assert result["market_price"] == 3200.0
    assert (
        result["execution"]["average_price"]
        == 3200.0
    )


def test_result_remains_simulated():
    result = bridge().execute(
        permission_result=granted_permission(),
        order=valid_order(),
    )

    assert result["test_trade"] is True
    assert result["simulated"] is True
    assert result["paper_trade"] is True
    assert result["live_order_submitted"] is False


def test_underlying_execution_remains_paper_trade():
    result = bridge().execute(
        permission_result=granted_permission(),
        order=valid_order(),
    )

    execution = result["execution"]

    assert execution["paper_trade"] is True
    assert execution["live_order_submitted"] is False
    assert execution["status"] == "FILLED"


def test_control_ids_are_preserved():
    result = bridge().execute(
        permission_result=granted_permission(),
        order=valid_order(),
    )

    assert result["approval_id"] == "ARB-002"
    assert result["permission_id"] == "PERM-002"


def test_exact_permitted_amount_is_required():
    result = bridge().execute(
        permission_result=granted_permission(
            trade_amount=0.2
        ),
        order=valid_order(
            quantity=0.1
        ),
    )

    assert result["executed"] is False
    assert (
        result["reason"]
        == "permitted_trade_amount_mismatch"
    )


def test_permission_must_be_granted():
    permission = granted_permission()
    permission["permission_granted"] = False

    result = bridge().execute(
        permission_result=permission,
        order=valid_order(),
    )

    assert result["executed"] is False
    assert (
        result["reason"]
        == "execution_permission_required"
    )


def test_permission_status_must_be_execution_permitted():
    permission = granted_permission()
    permission["status"] = (
        "awaiting_execution_permission"
    )

    result = bridge().execute(
        permission_result=permission,
        order=valid_order(),
    )

    assert result["executed"] is False
    assert (
        result["reason"]
        == "execution_permission_status_required"
    )


def test_live_submitted_permission_is_blocked():
    permission = granted_permission()
    permission["live_order_submitted"] = True

    result = bridge().execute(
        permission_result=permission,
        order=valid_order(),
    )

    assert result["executed"] is False
    assert (
        result["reason"]
        == "live_order_already_submitted"
    )
    assert result["live_order_submitted"] is False


def test_permission_id_is_required():
    permission = granted_permission()
    permission["permission_id"] = ""

    result = bridge().execute(
        permission_result=permission,
        order=valid_order(),
    )

    assert result["executed"] is False
    assert result["reason"] == "permission_id_required"


def test_approval_id_is_required():
    permission = granted_permission()
    permission["approval_id"] = ""

    result = bridge().execute(
        permission_result=permission,
        order=valid_order(),
    )

    assert result["executed"] is False
    assert result["reason"] == "approval_id_required"


def test_invalid_permitted_amount_is_blocked():
    result = bridge().execute(
        permission_result=granted_permission(
            trade_amount=0.0
        ),
        order=valid_order(),
    )

    assert result["executed"] is False
    assert (
        result["reason"]
        == "invalid_permitted_trade_amount"
    )


def test_invalid_order_amount_is_blocked():
    result = bridge().execute(
        permission_result=granted_permission(),
        order=valid_order(
            quantity=0.0
        ),
    )

    assert result["executed"] is False
    assert (
        result["reason"]
        == "invalid_order_trade_amount"
    )


def test_trade_amount_field_can_supply_amount():
    order = valid_order()
    del order["quantity"]
    order["trade_amount"] = 0.2

    result = bridge().execute(
        permission_result=granted_permission(),
        order=order,
    )

    assert result["executed"] is True
    assert result["trade_amount"] == 0.2


def test_symbol_is_normalized_before_market_lookup():
    provider = FakeMarketDataProvider()

    order = valid_order()
    order["symbol"] = " eth/usdt "

    result = bridge(
        provider
    ).execute(
        permission_result=granted_permission(),
        order=order,
    )

    assert result["executed"] is True
    assert provider.requested_symbols == [
        "ETH/USDT"
    ]


def test_missing_market_price_is_rejected():
    provider = FakeMarketDataProvider(
        prices={}
    )

    with pytest.raises(
        ValueError,
        match="market price unavailable",
    ):
        bridge(provider).execute(
            permission_result=granted_permission(),
            order=valid_order(),
        )


def test_missing_symbol_is_rejected():
    order = valid_order()
    del order["symbol"]

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        bridge().execute(
            permission_result=granted_permission(),
            order=order,
        )


def test_invalid_side_is_rejected():
    order = valid_order()
    order["side"] = "hold"

    with pytest.raises(
        ValueError,
        match="valid side is required",
    ):
        bridge().execute(
            permission_result=granted_permission(),
            order=order,
        )


def test_missing_permission_result_is_rejected():
    with pytest.raises(
        ValueError,
        match="permission_result is required",
    ):
        bridge().execute(
            permission_result=None,
            order=valid_order(),
        )


def test_missing_order_is_rejected():
    with pytest.raises(
        ValueError,
        match="order is required",
    ):
        bridge().execute(
            permission_result=granted_permission(),
            order=None,
        )


def test_market_provider_is_required():
    with pytest.raises(
        ValueError,
        match="market_data_provider is required",
    ):
        LiveMarketRepeatScalePaperBridge(
            None
        )


def test_execution_is_recorded_in_history():
    paper_bridge = bridge()

    paper_bridge.execute(
        permission_result=granted_permission(),
        order=valid_order(),
    )

    history = paper_bridge.history()

    assert len(history) == 1
    assert history[0]["executed"] is True


def test_blocked_execution_is_not_recorded_as_fill():
    paper_bridge = bridge()

    permission = granted_permission()
    permission["permission_granted"] = False

    paper_bridge.execute(
        permission_result=permission,
        order=valid_order(),
    )

    assert paper_bridge.history() == []


def test_real_single_use_permission_output_is_accepted():
    permission_gate = (
        StagedTestTradeExecutionPermission()
    )

    permission = permission_gate.create(
        handoff_result={
            "handoff_ready": True,
            "approval_id": "ARB-002",
            "asset": "ETH",
            "trade_amount": 0.2,
            "live_order_submitted": False,
        }
    )

    granted = permission_gate.grant(
        permission_id=permission["permission_id"],
        trade_amount=0.2,
    )

    result = bridge().execute(
        permission_result=granted,
        order=valid_order(),
    )

    assert granted["permission_granted"] is True
    assert result["executed"] is True
    assert result["live_order_submitted"] is False


def test_live_market_execution_never_submits_live_order():
    result = bridge().execute(
        permission_result=granted_permission(),
        order=valid_order(),
    )

    assert result["live_order_submitted"] is False
    assert (
        result["execution"]["live_order_submitted"]
        is False
    )


@pytest.mark.parametrize(
    "trade_amount",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
        0.0,
        -1.0,
    ],
)
def test_invalid_permitted_trade_amount_values_are_blocked(
    trade_amount,
):
    permission = granted_permission()
    permission["trade_amount"] = trade_amount

    result = bridge().execute(
        permission_result=permission,
        order=valid_order(),
    )

    assert result["executed"] is False
    assert (
        result["reason"]
        == "invalid_permitted_trade_amount"
    )
    assert result["live_order_submitted"] is False


def test_missing_permitted_trade_amount_is_blocked():
    permission = granted_permission()
    del permission["trade_amount"]

    result = bridge().execute(
        permission_result=permission,
        order=valid_order(),
    )

    assert result["executed"] is False
    assert (
        result["reason"]
        == "invalid_permitted_trade_amount"
    )


@pytest.mark.parametrize(
    "order_amount",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
        0.0,
        -1.0,
    ],
)
def test_invalid_order_trade_amount_values_are_blocked(
    order_amount,
):
    order = valid_order()
    order["quantity"] = order_amount

    result = bridge().execute(
        permission_result=granted_permission(),
        order=order,
    )

    assert result["executed"] is False
    assert (
        result["reason"]
        == "invalid_order_trade_amount"
    )
    assert result["live_order_submitted"] is False


def test_missing_order_amount_is_blocked():
    order = valid_order()
    order.pop("quantity", None)
    order.pop("trade_amount", None)

    result = bridge().execute(
        permission_result=granted_permission(),
        order=order,
    )

    assert result["executed"] is False
    assert (
        result["reason"]
        == "invalid_order_trade_amount"
    )


def test_explicit_none_trade_amount_does_not_fallback_to_quantity():
    order = valid_order()
    order["trade_amount"] = None
    order["quantity"] = granted_permission()[
        "trade_amount"
    ]

    result = bridge().execute(
        permission_result=granted_permission(),
        order=order,
    )

    assert result["executed"] is False
    assert (
        result["reason"]
        == "invalid_order_trade_amount"
    )


def test_numeric_string_amounts_are_normalized():
    permission = granted_permission()
    permission["trade_amount"] = "0.2"

    order = valid_order()
    order["quantity"] = "0.2"

    result = bridge().execute(
        permission_result=permission,
        order=order,
    )

    assert result["executed"] is True
    assert result["trade_amount"] == 0.2
