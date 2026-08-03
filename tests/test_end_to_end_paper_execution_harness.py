import pytest

from exchanges.end_to_end_paper_execution_harness import (
    EndToEndPaperExecutionHarness,
)


class FakeMarketDataProvider:
    def __init__(self, prices=None):
        self.prices = prices if prices is not None else {"BTC/USDT": 62000.0}

    def get_price(self, symbol):
        return self.prices.get(symbol)


@pytest.fixture
def harness():
    return EndToEndPaperExecutionHarness(FakeMarketDataProvider())


def valid_order():
    return {
        "symbol": "BTC/USDT",
        "side": "buy",
        "order_type": "market",
        "quantity": 0.01,
        "price": None,
    }


def test_valid_order_completes_full_paper_flow(harness):
    result = harness.execute(
        execution_id="EXEC-001",
        order=valid_order(),
    )

    assert result["status"] == "FILLED"
    assert result["paper_trade"] is True


def test_live_market_price_is_used(harness):
    result = harness.execute(
        execution_id="EXEC-001",
        order=valid_order(),
    )

    assert result["average_price"] == 62000.0


def test_execution_id_is_preserved(harness):
    result = harness.execute(
        execution_id="EXEC-123",
        order=valid_order(),
    )

    assert result["execution_id"] == "EXEC-123"


def test_missing_execution_id_is_rejected(harness):
    with pytest.raises(ValueError, match="execution_id is required"):
        harness.execute(execution_id="", order=valid_order())


def test_missing_order_is_rejected(harness):
    with pytest.raises(ValueError, match="order is required"):
        harness.execute(execution_id="EXEC-001", order=None)


def test_missing_symbol_is_rejected(harness):
    order = valid_order()
    del order["symbol"]

    with pytest.raises(ValueError):
        harness.execute(execution_id="EXEC-001", order=order)


def test_history_contains_completed_execution(harness):
    harness.execute(execution_id="EXEC-001", order=valid_order())

    assert len(harness.history()) == 1


def test_each_execution_is_unique(harness):
    first = harness.execute(execution_id="EXEC-001", order=valid_order())
    second = harness.execute(execution_id="EXEC-002", order=valid_order())

    assert first["paper_order_id"] != second["paper_order_id"]
