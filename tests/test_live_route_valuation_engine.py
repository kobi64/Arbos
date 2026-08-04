import pytest

from exchanges.live_route_valuation_engine import (
    LiveRouteValuationEngine,
)


class FakeMarketDataProvider:
    def __init__(self):
        self.prices = {
            "BTC/USDT": {"bid": 61900.0, "ask": 62000.0},
            "ETH/BTC": {"bid": 0.049, "ask": 0.05},
            "ETH/USDT": {"bid": 3200.0, "ask": 3210.0},
        }

    def get_bid(self, symbol):
        return self.prices[symbol]["bid"]

    def get_ask(self, symbol):
        return self.prices[symbol]["ask"]


@pytest.fixture
def engine():
    return LiveRouteValuationEngine(FakeMarketDataProvider())


def valid_route():
    return {
        "route_id": "ROUTE-001",
        "legs": [
            {"symbol": "BTC/USDT", "side": "buy"},
            {"symbol": "ETH/BTC", "side": "buy"},
            {"symbol": "ETH/USDT", "side": "sell"},
        ],
    }


def test_sequential_route_valuation_uses_ask_for_buys_and_bid_for_sells(engine):
    result = engine.evaluate(
        route=valid_route(),
        starting_value=1000.0,
    )

    assert result["route_id"] == "ROUTE-001"
    assert result["starting_value"] == 1000.0
    assert result["gross_final_value"] > 0
    assert len(result["legs"]) == 3


def test_sequential_amounts_are_carried_between_legs(engine):
    result = engine.evaluate(
        route=valid_route(),
        starting_value=1000.0,
    )

    assert result["legs"][0]["output_amount"] == pytest.approx(1000.0 / 62000.0)
    assert result["legs"][1]["output_amount"] == pytest.approx((1000.0 / 62000.0) / 0.05)
    assert result["gross_final_value"] == pytest.approx(((1000.0 / 62000.0) / 0.05) * 3200.0)


def test_missing_route_is_rejected(engine):
    with pytest.raises(ValueError, match="route is required"):
        engine.evaluate(route=None, starting_value=1000.0)


def test_invalid_starting_value_is_rejected(engine):
    with pytest.raises(ValueError, match="starting_value must be positive"):
        engine.evaluate(route=valid_route(), starting_value=0.0)


def test_invalid_side_is_rejected(engine):
    route = valid_route()
    route["legs"][0]["side"] = "hold"

    with pytest.raises(ValueError, match="invalid side"):
        engine.evaluate(route=route, starting_value=1000.0)
