import pytest

from core.fee_aware_live_triangle_scanner import (
    FeeAwareLiveTriangleScanner,
)


class FakeMarketDataProvider:
    def __init__(self):
        self.prices = {
            "BTC/USDT": {"bid": 64850.0, "ask": 64860.0},
            "ETH/BTC": {"bid": 0.02940, "ask": 0.02950},
            "ETH/USDT": {"bid": 1912.0, "ask": 1913.0},
            "SOL/BTC": {"bid": 0.00114, "ask": 0.00115},
            "SOL/USDT": {"bid": 74.0, "ask": 74.1},
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


def test_scans_routes_with_fees_and_ranks_by_net_profit():
    scanner = FeeAwareLiveTriangleScanner(FakeMarketDataProvider())

    results = scanner.scan(
        routes=sample_routes(),
        starting_value=100.0,
        fee_rate=0.004,
    )

    assert len(results) == 2
    assert results[0]["net_profit_percent"] >= results[1]["net_profit_percent"]
    assert results[0]["paper_only"] is True
    assert results[0]["live_order_submitted"] is False


def test_result_exposes_fee_aware_values():
    scanner = FeeAwareLiveTriangleScanner(FakeMarketDataProvider())

    result = scanner.scan(
        routes=sample_routes(),
        starting_value=100.0,
        fee_rate=0.004,
    )[0]

    assert "net_final_value" in result
    assert "net_profit" in result
    assert "net_profit_percent" in result
    assert "total_fee_rate_effect" in result
    assert len(result["legs"]) == 3


def test_rejects_negative_fee_rate():
    scanner = FeeAwareLiveTriangleScanner(FakeMarketDataProvider())

    with pytest.raises(ValueError, match="fee_rate must be non-negative"):
        scanner.scan(
            routes=sample_routes(),
            starting_value=100.0,
            fee_rate=-0.001,
        )


def test_rejects_non_positive_starting_value():
    scanner = FeeAwareLiveTriangleScanner(FakeMarketDataProvider())

    with pytest.raises(ValueError, match="starting_value must be positive"):
        scanner.scan(
            routes=sample_routes(),
            starting_value=0,
            fee_rate=0.004,
        )
