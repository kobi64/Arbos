import pytest

from exchanges.paper_arbitrage_route_execution import (
    PaperArbitrageRouteExecutionCoordinator,
)


class FakeMarketDataProvider:
    def __init__(self, prices=None):
        self.prices = prices or {
            "BTC/USDT": 62000.0,
            "ETH/BTC": 0.05,
            "ETH/USDT": 3200.0,
        }

    def get_price(self, symbol):
        return self.prices.get(symbol)


@pytest.fixture
def coordinator():
    return PaperArbitrageRouteExecutionCoordinator(FakeMarketDataProvider())


def valid_route():
    return {
        "route_id": "ROUTE-001",
        "legs": [
            {"symbol": "BTC/USDT", "side": "buy", "quantity": 0.01},
            {"symbol": "ETH/BTC", "side": "buy", "quantity": 0.2},
            {"symbol": "ETH/USDT", "side": "sell", "quantity": 0.2},
        ],
    }


def test_valid_route_executes_all_legs(coordinator):
    result = coordinator.execute(valid_route())

    assert result["status"] == "COMPLETED"
    assert len(result["legs"]) == 3


def test_route_id_is_preserved(coordinator):
    result = coordinator.execute(valid_route())

    assert result["route_id"] == "ROUTE-001"


def test_each_leg_uses_live_market_price(coordinator):
    result = coordinator.execute(valid_route())

    assert result["legs"][0]["average_price"] == 62000.0
    assert result["legs"][1]["average_price"] == 0.05
    assert result["legs"][2]["average_price"] == 3200.0


def test_missing_route_is_rejected(coordinator):
    with pytest.raises(ValueError, match="route is required"):
        coordinator.execute(None)


def test_missing_route_id_is_rejected(coordinator):
    route = valid_route()
    del route["route_id"]

    with pytest.raises(ValueError, match="route_id is required"):
        coordinator.execute(route)


def test_missing_legs_is_rejected(coordinator):
    route = valid_route()
    del route["legs"]

    with pytest.raises(ValueError, match="legs are required"):
        coordinator.execute(route)


def test_history_records_completed_route(coordinator):
    coordinator.execute(valid_route())

    assert len(coordinator.history()) == 1


def test_each_leg_is_marked_as_paper_trade(coordinator):
    result = coordinator.execute(valid_route())

    assert all(leg["paper_trade"] is True for leg in result["legs"])
