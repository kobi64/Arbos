import pytest

from exchanges.scanner_paper_execution_coordinator import (
    ScannerPaperExecutionCoordinator,
)


class FakeMarketDataProvider:
    def __init__(self, prices=None):
        self.prices = prices if prices is not None else {"BTC/USDT": 62000.0}

    def get_price(self, symbol):
        return self.prices.get(symbol)


@pytest.fixture
def coordinator():
    return ScannerPaperExecutionCoordinator(FakeMarketDataProvider())


def valid_opportunity():
    return {
        "opportunity_id": "OPP-001",
        "symbol": "BTC/USDT",
        "side": "buy",
        "order_type": "market",
        "quantity": 0.01,
    }


def test_valid_opportunity_executes_as_paper_trade(coordinator):
    result = coordinator.execute(valid_opportunity())

    assert result["status"] == "FILLED"
    assert result["paper_trade"] is True


def test_opportunity_id_is_preserved(coordinator):
    result = coordinator.execute(valid_opportunity())

    assert result["opportunity_id"] == "OPP-001"


def test_live_market_price_is_used(coordinator):
    result = coordinator.execute(valid_opportunity())

    assert result["average_price"] == 62000.0


def test_missing_opportunity_is_rejected(coordinator):
    with pytest.raises(ValueError, match="opportunity is required"):
        coordinator.execute(None)


def test_missing_opportunity_id_is_rejected(coordinator):
    opportunity = valid_opportunity()
    del opportunity["opportunity_id"]

    with pytest.raises(ValueError, match="opportunity_id is required"):
        coordinator.execute(opportunity)


def test_missing_symbol_is_rejected(coordinator):
    opportunity = valid_opportunity()
    del opportunity["symbol"]

    with pytest.raises(ValueError):
        coordinator.execute(opportunity)


def test_history_records_execution(coordinator):
    coordinator.execute(valid_opportunity())

    assert len(coordinator.history()) == 1


def test_each_execution_gets_unique_paper_order_id(coordinator):
    first = coordinator.execute(valid_opportunity())
    second = coordinator.execute(valid_opportunity())

    assert first["paper_order_id"] != second["paper_order_id"]
