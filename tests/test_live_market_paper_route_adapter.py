import pytest

from exchanges.live_market_paper_route_adapter import (
    LiveMarketPaperRouteAdapter,
)


class FakeLiveMarketDataProvider:
    def __init__(self, prices=None):
        self.prices = prices or {
            "BTC/USDT": 62000.0,
            "ETH/BTC": 0.05,
            "ETH/USDT": 3200.0,
        }

    def get_price(self, symbol):
        return self.prices.get(symbol)


@pytest.fixture
def adapter():
    return LiveMarketPaperRouteAdapter(FakeLiveMarketDataProvider())


def valid_route():
    return {
        "route_id": "ROUTE-001",
        "legs": [
            {"symbol": "BTC/USDT", "side": "buy", "quantity": 0.01},
            {"symbol": "ETH/BTC", "side": "buy", "quantity": 0.2},
            {"symbol": "ETH/USDT", "side": "sell", "quantity": 0.2},
        ],
    }


def test_live_prices_are_attached_to_route(adapter):
    result = adapter.adapt(valid_route())

    assert result["legs"][0]["market_price"] == 62000.0
    assert result["legs"][1]["market_price"] == 0.05
    assert result["legs"][2]["market_price"] == 3200.0


def test_route_id_is_preserved(adapter):
    result = adapter.adapt(valid_route())

    assert result["route_id"] == "ROUTE-001"


def test_missing_route_is_rejected(adapter):
    with pytest.raises(ValueError, match="route is required"):
        adapter.adapt(None)


def test_missing_market_price_is_rejected():
    provider = FakeLiveMarketDataProvider({"BTC/USDT": 62000.0})
    adapter = LiveMarketPaperRouteAdapter(provider)

    with pytest.raises(ValueError, match="market price unavailable"):
        adapter.adapt(valid_route())


def test_original_leg_details_are_preserved(adapter):
    result = adapter.adapt(valid_route())

    first_leg = result["legs"][0]
    assert first_leg["symbol"] == "BTC/USDT"
    assert first_leg["side"] == "buy"
    assert first_leg["quantity"] == 0.01


def test_adapted_route_is_marked_as_live_market(adapter):
    result = adapter.adapt(valid_route())

    assert result["live_market"] is True
