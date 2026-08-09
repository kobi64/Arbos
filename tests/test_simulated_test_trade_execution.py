import pytest

from core.simulated_test_trade_execution import (
    SimulatedTestTradeExecution,
)


class FakeMarketDataProvider:
    def __init__(self, prices=None):
        self.prices = (
            prices
            if prices is not None
            else {"ETH/USDT": 3100.0}
        )

    def get_price(self, symbol):
        return self.prices.get(symbol)


def accepted_order():
    return {
        "accepted": True,
        "reason": "test_trade_order_record_created",
        "order_id": "order-1",
        "route_id": "DIRECT-ETH",
        "approval_id": "ARB-001",
        "permission_id": "PERM-001",
        "test_trade": True,
        "live_order_submitted": False,
    }


def internal_order():
    return {
        "order_id": "order-1",
        "exchange": "HTX",
        "symbol": "ETH/USDT",
        "side": "BUY",
        "amount": 0.05,
        "status": "CREATED",
    }


def test_accepted_test_trade_executes_as_paper_trade():
    executor = SimulatedTestTradeExecution(
        FakeMarketDataProvider()
    )

    result = executor.execute(
        submission_result=accepted_order(),
        order_record=internal_order(),
    )

    assert result["simulated"] is True
    assert result["status"] == "FILLED"
    assert result["paper_trade"] is True
    assert result["live_order_submitted"] is False


def test_live_market_price_is_used():
    executor = SimulatedTestTradeExecution(
        FakeMarketDataProvider(
            {"ETH/USDT": 3200.0}
        )
    )

    result = executor.execute(
        submission_result=accepted_order(),
        order_record=internal_order(),
    )

    assert result["average_price"] == 3200.0
    assert result["market_price"] == 3200.0


def test_control_identifiers_are_preserved():
    executor = SimulatedTestTradeExecution(
        FakeMarketDataProvider()
    )

    result = executor.execute(
        submission_result=accepted_order(),
        order_record=internal_order(),
    )

    assert result["order_id"] == "order-1"
    assert result["route_id"] == "DIRECT-ETH"
    assert result["approval_id"] == "ARB-001"
    assert result["permission_id"] == "PERM-001"


def test_unaccepted_submission_is_blocked():
    executor = SimulatedTestTradeExecution(
        FakeMarketDataProvider()
    )

    submission = accepted_order()
    submission["accepted"] = False

    result = executor.execute(
        submission_result=submission,
        order_record=internal_order(),
    )

    assert result["simulated"] is False
    assert result["reason"] == "order_submission_not_accepted"
    assert result["live_order_submitted"] is False


def test_non_test_trade_is_blocked():
    executor = SimulatedTestTradeExecution(
        FakeMarketDataProvider()
    )

    submission = accepted_order()
    submission["test_trade"] = False

    result = executor.execute(
        submission_result=submission,
        order_record=internal_order(),
    )

    assert result["simulated"] is False
    assert result["reason"] == "test_trade_required"
    assert result["live_order_submitted"] is False


def test_order_id_must_match_submission():
    executor = SimulatedTestTradeExecution(
        FakeMarketDataProvider()
    )

    order = internal_order()
    order["order_id"] = "order-999"

    result = executor.execute(
        submission_result=accepted_order(),
        order_record=order,
    )

    assert result["simulated"] is False
    assert result["reason"] == "order_id_mismatch"
    assert result["live_order_submitted"] is False


def test_existing_live_submission_is_blocked():
    executor = SimulatedTestTradeExecution(
        FakeMarketDataProvider()
    )

    submission = accepted_order()
    submission["live_order_submitted"] = True

    result = executor.execute(
        submission_result=submission,
        order_record=internal_order(),
    )

    assert result["simulated"] is False
    assert result["reason"] == "live_order_already_submitted"
    assert result["live_order_submitted"] is True


def test_missing_submission_result_is_rejected():
    executor = SimulatedTestTradeExecution(
        FakeMarketDataProvider()
    )

    with pytest.raises(
        ValueError,
        match="submission_result is required",
    ):
        executor.execute(
            submission_result=None,
            order_record=internal_order(),
        )


def test_missing_order_record_is_rejected():
    executor = SimulatedTestTradeExecution(
        FakeMarketDataProvider()
    )

    with pytest.raises(
        ValueError,
        match="order_record is required",
    ):
        executor.execute(
            submission_result=accepted_order(),
            order_record=None,
        )
