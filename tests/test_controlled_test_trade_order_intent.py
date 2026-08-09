import pytest

from core.controlled_test_trade_order_intent import (
    ControlledTestTradeOrderIntent,
)


def authorised_execution():
    return {
        "authorised": True,
        "reason": "execution_authorised",
        "permission_id": "PERM-001",
        "route_id": "DIRECT-ETH",
        "approval_id": "ARB-001",
        "asset": "ETH",
        "trade_amount": 250.0,
        "live_order_submitted": False,
    }


def test_builds_order_intent_from_authorised_test_trade():
    builder = ControlledTestTradeOrderIntent()

    result = builder.build(
        execution_result=authorised_execution(),
        exchange="kucoin",
        symbol="ETH/USDT",
        side="buy",
    )

    assert result["intent_ready"] is True
    assert result["reason"] == "order_intent_ready"
    assert result["exchange"] == "kucoin"
    assert result["symbol"] == "ETH/USDT"
    assert result["side"] == "buy"
    assert result["amount"] == 250.0
    assert result["test_trade"] is True
    assert result["live_order_submitted"] is False


def test_preserves_control_identifiers():
    builder = ControlledTestTradeOrderIntent()

    result = builder.build(
        execution_result=authorised_execution(),
        exchange="kucoin",
        symbol="ETH/USDT",
        side="buy",
    )

    assert result["route_id"] == "DIRECT-ETH"
    assert result["approval_id"] == "ARB-001"
    assert result["permission_id"] == "PERM-001"


def test_unauthorised_execution_cannot_create_intent():
    builder = ControlledTestTradeOrderIntent()

    execution = authorised_execution()
    execution["authorised"] = False

    result = builder.build(
        execution_result=execution,
        exchange="kucoin",
        symbol="ETH/USDT",
        side="buy",
    )

    assert result["intent_ready"] is False
    assert result["reason"] == "execution_not_authorised"
    assert result["live_order_submitted"] is False


def test_existing_live_submission_blocks_intent():
    builder = ControlledTestTradeOrderIntent()

    execution = authorised_execution()
    execution["live_order_submitted"] = True

    result = builder.build(
        execution_result=execution,
        exchange="kucoin",
        symbol="ETH/USDT",
        side="buy",
    )

    assert result["intent_ready"] is False
    assert result["reason"] == "live_order_already_submitted"
    assert result["live_order_submitted"] is True


def test_invalid_side_is_rejected():
    builder = ControlledTestTradeOrderIntent()

    with pytest.raises(
        ValueError,
        match="side must be buy or sell",
    ):
        builder.build(
            execution_result=authorised_execution(),
            exchange="kucoin",
            symbol="ETH/USDT",
            side="hold",
        )


def test_missing_execution_result_is_rejected():
    builder = ControlledTestTradeOrderIntent()

    with pytest.raises(
        ValueError,
        match="execution_result is required",
    ):
        builder.build(
            execution_result=None,
            exchange="kucoin",
            symbol="ETH/USDT",
            side="buy",
        )
