import pytest

from core.controlled_live_triangle_scanner import (
    ControlledLiveTriangleScanner,
)


class FakeMarketDataProvider:
    def __init__(self):
        self.prices = {
            "BTC/USDT": {"bid": 64850.0, "ask": 64860.0},
            "ETH/BTC": {"bid": 0.02940, "ask": 0.02950},
            "ETH/USDT": {"bid": 1912.0, "ask": 1913.0},
            "SOL/BTC": {"bid": 0.00210, "ask": 0.00211},
            "SOL/USDT": {"bid": 136.8, "ask": 137.0},
        }

    def get_bid(self, symbol):
        return self.prices[symbol]["bid"]

    def get_ask(self, symbol):
        return self.prices[symbol]["ask"]


def sample_routes():
    return [
        {
            "route_id": "BTC-ETH",
            "legs": [
                {"symbol": "BTC/USDT", "side": "buy"},
                {"symbol": "ETH/BTC", "side": "buy"},
                {"symbol": "ETH/USDT", "side": "sell"},
            ],
        },
        {
            "route_id": "BTC-SOL",
            "legs": [
                {"symbol": "BTC/USDT", "side": "buy"},
                {"symbol": "SOL/BTC", "side": "buy"},
                {"symbol": "SOL/USDT", "side": "sell"},
            ],
        },
    ]


def test_scans_and_ranks_routes_by_profit_percent():
    scanner = ControlledLiveTriangleScanner(FakeMarketDataProvider())

    results = scanner.scan(
        routes=sample_routes(),
        starting_value=100.0,
    )

    assert len(results) == 2
    assert results[0]["profit_percent"] >= results[1]["profit_percent"]
    assert results[0]["paper_only"] is True
    assert results[0]["live_order_submitted"] is False


def test_route_result_contains_live_bid_ask_valuation():
    scanner = ControlledLiveTriangleScanner(FakeMarketDataProvider())

    results = scanner.scan(
        routes=sample_routes(),
        starting_value=100.0,
    )

    first = results[0]

    assert "route_id" in first
    assert "starting_value" in first
    assert "final_value" in first
    assert "net_profit" in first
    assert "profit_percent" in first
    assert len(first["legs"]) == 3


def test_rejects_non_positive_starting_value():
    scanner = ControlledLiveTriangleScanner(FakeMarketDataProvider())

    with pytest.raises(ValueError, match="starting_value must be positive"):
        scanner.scan(
            routes=sample_routes(),
            starting_value=0,
        )
