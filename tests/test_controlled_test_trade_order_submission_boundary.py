import pytest

from core.controlled_test_trade_order_submission_boundary import (
    ControlledTestTradeOrderSubmissionBoundary,
)


def ready_intent():
    return {
        "intent_ready": True,
        "reason": "order_intent_ready",
        "exchange": "HTX",
        "buy_exchange": "htx",
        "sell_exchange": "htx",
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


@pytest.mark.parametrize(
    "amount",
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
def test_submission_rejects_invalid_order_amount(
    amount,
):
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    intent = ready_intent()
    intent["amount"] = amount

    result = boundary.submit(intent)

    assert result["accepted"] is False
    assert result["reason"] == "invalid_order_amount"


def test_submission_supports_numeric_string_amount():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    intent = ready_intent()
    intent["amount"] = "250"

    result = boundary.submit(intent)

    assert result["accepted"] is True

    order = boundary.get_order(
        result["order_id"]
    )

    assert order["amount"] == 250.0


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
        ("permission_id", None),
        ("permission_id", ""),
        ("permission_id", "   "),
        ("permission_id", 0),
        ("permission_id", False),
        ("asset", None),
        ("asset", ""),
        ("asset", "   "),
        ("asset", 0),
        ("asset", False),
    ],
)
def test_submission_requires_bound_identity(
    field,
    value,
):
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    intent = ready_intent()
    intent[field] = value

    result = boundary.submit(intent)

    assert result["accepted"] is False
    assert result["reason"] == f"{field}_required"


@pytest.mark.parametrize(
    "field,value",
    [
        ("exchange", None),
        ("exchange", ""),
        ("exchange", "   "),
        ("exchange", 0),
        ("exchange", False),
        ("symbol", None),
        ("symbol", ""),
        ("symbol", "   "),
        ("symbol", 0),
        ("symbol", False),
    ],
)
def test_submission_requires_order_destination(
    field,
    value,
):
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    intent = ready_intent()
    intent[field] = value

    result = boundary.submit(intent)

    assert result["accepted"] is False
    assert result["reason"] == f"{field}_required"


def test_submission_normalizes_identity_before_order_creation():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    intent = ready_intent()
    intent["route_id"] = "  DIRECT-ETH  "
    intent["approval_id"] = "  ARB-001  "
    intent["permission_id"] = "  PERM-001  "
    intent["asset"] = " eth "
    intent["exchange"] = " htx "
    intent["symbol"] = " eth/usdt "

    result = boundary.submit(intent)

    assert result["accepted"] is True
    assert result["route_id"] == "DIRECT-ETH"
    assert result["approval_id"] == "ARB-001"
    assert result["permission_id"] == "PERM-001"


def test_numeric_string_and_numeric_amount_duplicate_is_blocked():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    first = ready_intent()
    first["amount"] = "250"

    second = ready_intent()
    second["amount"] = 250.0

    accepted = boundary.submit(first)
    duplicate = boundary.submit(second)

    assert accepted["accepted"] is True
    assert duplicate["accepted"] is False
    assert duplicate["reason"] == "duplicate_order_intent_blocked"


# EX-331 — submission destination identity audit


def destination_bound_intent(
    *,
    side="buy",
    exchange=None,
):
    intent = ready_intent()
    intent["buy_exchange"] = "kucoin"
    intent["sell_exchange"] = "gate"
    intent["side"] = side

    if exchange is None:
        intent["exchange"] = (
            "kucoin"
            if side == "buy"
            else "gate"
        )
    else:
        intent["exchange"] = exchange

    return intent


def test_submission_accepts_bound_buy_destination():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    result = boundary.submit(
        destination_bound_intent(
            side="buy",
        )
    )

    assert result["accepted"] is True

    order = boundary.get_order(
        result["order_id"]
    )

    assert order["exchange"] == "KUCOIN"
    assert order["buy_exchange"] == "KUCOIN"
    assert order["sell_exchange"] == "GATE"


def test_submission_accepts_bound_sell_destination():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    result = boundary.submit(
        destination_bound_intent(
            side="sell",
        )
    )

    assert result["accepted"] is True

    order = boundary.get_order(
        result["order_id"]
    )

    assert order["exchange"] == "GATE"
    assert order["buy_exchange"] == "KUCOIN"
    assert order["sell_exchange"] == "GATE"


def test_submission_blocks_buy_destination_substitution():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    result = boundary.submit(
        destination_bound_intent(
            side="buy",
            exchange="gate",
        )
    )

    assert result["accepted"] is False
    assert result["reason"] == "buy_exchange_mismatch"
    assert result["live_order_submitted"] is False


def test_submission_blocks_sell_destination_substitution():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    result = boundary.submit(
        destination_bound_intent(
            side="sell",
            exchange="kucoin",
        )
    )

    assert result["accepted"] is False
    assert result["reason"] == "sell_exchange_mismatch"
    assert result["live_order_submitted"] is False


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
def test_submission_requires_approved_destination_identity(
    field,
    value,
):
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    intent = destination_bound_intent()
    intent[field] = value

    result = boundary.submit(intent)

    assert result["accepted"] is False
    assert result["reason"] == f"{field}_required"
    assert result["live_order_submitted"] is False


def test_submission_destination_comparison_is_normalized():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    intent = destination_bound_intent()
    intent["exchange"] = " KUCOIN "
    intent["buy_exchange"] = " kucoin "
    intent["sell_exchange"] = " gate "

    result = boundary.submit(intent)

    assert result["accepted"] is True

    order = boundary.get_order(
        result["order_id"]
    )

    assert order["exchange"] == "KUCOIN"
    assert order["buy_exchange"] == "KUCOIN"
    assert order["sell_exchange"] == "GATE"


def test_submission_destination_mismatch_creates_no_order():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    result = boundary.submit(
        destination_bound_intent(
            side="buy",
            exchange="gate",
        )
    )

    assert result["accepted"] is False
    assert result["live_order_submitted"] is False
    assert "order_id" not in result


# EX-332 — internal order record identity integrity audit


def test_internal_order_record_preserves_full_execution_identity():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    intent = destination_bound_intent(
        side="buy",
    )

    result = boundary.submit(intent)

    assert result["accepted"] is True

    order = boundary.get_order(
        result["order_id"]
    )

    assert order["route_id"] == "DIRECT-ETH"
    assert order["approval_id"] == "ARB-001"
    assert order["permission_id"] == "PERM-001"
    assert order["asset"] == "ETH"

    assert order["exchange"] == "KUCOIN"
    assert order["buy_exchange"] == "KUCOIN"
    assert order["sell_exchange"] == "GATE"

    assert order["symbol"] == "ETH/USDT"
    assert order["side"] == "BUY"
    assert order["amount"] == 250.0
    assert order["status"] == "CREATED"


def test_internal_order_identity_is_normalized_and_preserved():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    intent = destination_bound_intent(
        side="buy",
    )

    intent["route_id"] = "  DIRECT-ETH  "
    intent["approval_id"] = "  ARB-001  "
    intent["permission_id"] = "  PERM-001  "
    intent["asset"] = " eth "
    intent["exchange"] = " kucoin "
    intent["buy_exchange"] = " kucoin "
    intent["sell_exchange"] = " gate "
    intent["symbol"] = " eth/usdt "

    result = boundary.submit(intent)

    assert result["accepted"] is True

    order = boundary.get_order(
        result["order_id"]
    )

    assert order["route_id"] == "DIRECT-ETH"
    assert order["approval_id"] == "ARB-001"
    assert order["permission_id"] == "PERM-001"
    assert order["asset"] == "ETH"

    assert order["exchange"] == "KUCOIN"
    assert order["buy_exchange"] == "KUCOIN"
    assert order["sell_exchange"] == "GATE"

    assert order["symbol"] == "ETH/USDT"
    assert order["side"] == "BUY"


def test_internal_order_identity_is_independent_of_source_intent_mutation():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    intent = destination_bound_intent(
        side="buy",
    )

    result = boundary.submit(intent)

    assert result["accepted"] is True

    intent["route_id"] = "MUTATED-ROUTE"
    intent["approval_id"] = "MUTATED-APPROVAL"
    intent["permission_id"] = "MUTATED-PERMISSION"
    intent["asset"] = "BTC"
    intent["exchange"] = "GATE"
    intent["buy_exchange"] = "GATE"
    intent["sell_exchange"] = "KUCOIN"
    intent["symbol"] = "BTC/USDT"
    intent["side"] = "sell"
    intent["amount"] = 999.0

    order = boundary.get_order(
        result["order_id"]
    )

    assert order["route_id"] == "DIRECT-ETH"
    assert order["approval_id"] == "ARB-001"
    assert order["permission_id"] == "PERM-001"
    assert order["asset"] == "ETH"

    assert order["exchange"] == "KUCOIN"
    assert order["buy_exchange"] == "KUCOIN"
    assert order["sell_exchange"] == "GATE"

    assert order["symbol"] == "ETH/USDT"
    assert order["side"] == "BUY"
    assert order["amount"] == 250.0


def test_internal_order_identity_survives_status_update():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    result = boundary.submit(
        destination_bound_intent(
            side="buy",
        )
    )

    assert result["accepted"] is True

    order_id = result["order_id"]

    boundary._orders.update_status(
        order_id,
        "FILLED",
    )

    order = boundary.get_order(order_id)

    assert order["status"] == "FILLED"

    assert order["route_id"] == "DIRECT-ETH"
    assert order["approval_id"] == "ARB-001"
    assert order["permission_id"] == "PERM-001"
    assert order["asset"] == "ETH"

    assert order["exchange"] == "KUCOIN"
    assert order["buy_exchange"] == "KUCOIN"
    assert order["sell_exchange"] == "GATE"

    assert order["symbol"] == "ETH/USDT"
    assert order["side"] == "BUY"
    assert order["amount"] == 250.0


def test_internal_order_identity_survives_cancel():
    boundary = ControlledTestTradeOrderSubmissionBoundary()

    result = boundary.submit(
        destination_bound_intent(
            side="sell",
        )
    )

    assert result["accepted"] is True

    order_id = result["order_id"]

    boundary._orders.cancel_order(
        order_id
    )

    order = boundary.get_order(order_id)

    assert order["status"] == "CANCELLED"

    assert order["route_id"] == "DIRECT-ETH"
    assert order["approval_id"] == "ARB-001"
    assert order["permission_id"] == "PERM-001"
    assert order["asset"] == "ETH"

    assert order["exchange"] == "GATE"
    assert order["buy_exchange"] == "KUCOIN"
    assert order["sell_exchange"] == "GATE"

    assert order["symbol"] == "ETH/USDT"
    assert order["side"] == "SELL"
    assert order["amount"] == 250.0
