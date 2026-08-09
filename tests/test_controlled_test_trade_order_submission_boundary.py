import pytest

from core.controlled_test_trade_order_submission_boundary import (
    ControlledTestTradeOrderSubmissionBoundary,
)


def ready_intent():
    return {
        "intent_ready": True,
        "reason": "order_intent_ready",
        "exchange": "HTX",
        "symbol": "ETH/USDT",
        "side": "buy",
        "amount": 250.0,
        "asset": "ETH",
        "route_id": "DIRECT-ETH",
        "approval_id": "ARB-001",
        "permission_id": "PERM-001",
        "test_trade": True,
        "live_order_submitted": False,
    }


def test_ready_intent_creates_internal_order_record():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    result = boundary.submit(
        order_intent=ready_intent(),
    )

    assert result["accepted"] is True
    assert result["reason"] == "test_trade_order_record_created"
    assert result["order_id"].startswith("order-")
    assert result["route_id"] == "DIRECT-ETH"
    assert result["live_order_submitted"] is False


def test_internal_order_preserves_trade_details():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    result = boundary.submit(
        order_intent=ready_intent(),
    )

    order = boundary.get_order(
        result["order_id"]
    )

    assert order["exchange"] == "HTX"
    assert order["symbol"] == "ETH/USDT"
    assert order["side"] == "BUY"
    assert order["amount"] == 250.0
    assert order["status"] == "CREATED"


def test_non_ready_intent_is_blocked():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    intent = ready_intent()
    intent["intent_ready"] = False

    result = boundary.submit(
        order_intent=intent,
    )

    assert result["accepted"] is False
    assert result["reason"] == "order_intent_not_ready"
    assert result["live_order_submitted"] is False


def test_non_test_trade_is_blocked():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    intent = ready_intent()
    intent["test_trade"] = False

    result = boundary.submit(
        order_intent=intent,
    )

    assert result["accepted"] is False
    assert result["reason"] == "test_trade_required"
    assert result["live_order_submitted"] is False


def test_existing_live_submission_is_blocked():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    intent = ready_intent()
    intent["live_order_submitted"] = True

    result = boundary.submit(
        order_intent=intent,
    )

    assert result["accepted"] is False
    assert result["reason"] == "live_order_already_submitted"
    assert result["live_order_submitted"] is True


def test_duplicate_intent_is_blocked():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    intent = ready_intent()

    first = boundary.submit(
        order_intent=intent,
    )

    second = boundary.submit(
        order_intent=intent,
    )

    assert first["accepted"] is True
    assert second["accepted"] is False
    assert second["reason"] == "duplicate_order_intent_blocked"
    assert second["live_order_submitted"] is False


def test_missing_order_intent_is_rejected():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    with pytest.raises(
        ValueError,
        match="order_intent is required",
    ):
        boundary.submit(
            order_intent=None,
        )


def test_boundary_does_not_submit_live_order():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    result = boundary.submit(
        order_intent=ready_intent(),
    )

    assert result["accepted"] is True
    assert result["live_order_submitted"] is False
    assert "exchange_order_id" not in result
