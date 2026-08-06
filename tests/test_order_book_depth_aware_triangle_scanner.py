import pytest

from core.order_book_depth_aware_triangle_scanner import (
    OrderBookDepthAwareTriangleScanner,
)


class FakeOrderBookProvider:
    def __init__(self):
        self.books = {
            "BTC/USDT": {
                "bids": [[64850.0, 1.0]],
                "asks": [[64860.0, 0.001], [64870.0, 1.0]],
            },
            "ETH/BTC": {
                "bids": [[0.02940, 10.0]],
                "asks": [[0.02950, 0.02], [0.02960, 10.0]],
            },
            "ETH/USDT": {
                "bids": [[1912.0, 0.02], [1911.0, 10.0]],
                "asks": [[1913.0, 10.0]],
            },
        }

    def snapshot(self, symbol):
        return self.books[symbol]


def valid_route():
    return {
        "route_id": "DEPTH-ETH",
        "legs": [
            {"symbol": "BTC/USDT", "side": "buy"},
            {"symbol": "ETH/BTC", "side": "buy"},
            {"symbol": "ETH/USDT", "side": "sell"},
        ],
    }


def test_scans_route_using_order_book_depth():
    scanner = OrderBookDepthAwareTriangleScanner(
        FakeOrderBookProvider()
    )

    result = scanner.scan_route(
        route=valid_route(),
        starting_value=100.0,
        fee_rate=0.004,
        max_slippage_percent=1.0,
    )

    assert result["route_id"] == "DEPTH-ETH"
    assert result["filled"] is True
    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False
    assert len(result["legs"]) == 3


def test_result_exposes_depth_fee_and_slippage_values():
    scanner = OrderBookDepthAwareTriangleScanner(
        FakeOrderBookProvider()
    )

    result = scanner.scan_route(
        route=valid_route(),
        starting_value=100.0,
        fee_rate=0.004,
        max_slippage_percent=1.0,
    )

    assert "net_final_value" in result
    assert "net_profit" in result
    assert "net_profit_percent" in result
    assert "total_fee_amount" in result
    assert "max_leg_slippage_percent" in result
    assert result["max_leg_slippage_percent"] >= 0


def test_rejects_route_when_liquidity_is_insufficient():
    provider = FakeOrderBookProvider()
    provider.books["BTC/USDT"] = {
        "bids": [[64850.0, 1.0]],
        "asks": [[64860.0, 0.0001]],
    }

    scanner = OrderBookDepthAwareTriangleScanner(provider)

    result = scanner.scan_route(
        route=valid_route(),
        starting_value=100.0,
        fee_rate=0.004,
        max_slippage_percent=1.0,
    )

    assert result["filled"] is False
    assert result["reason"] == "insufficient_liquidity"


def test_rejects_route_when_slippage_exceeds_limit():
    scanner = OrderBookDepthAwareTriangleScanner(
        FakeOrderBookProvider()
    )

    result = scanner.scan_route(
        route=valid_route(),
        starting_value=100.0,
        fee_rate=0.004,
        max_slippage_percent=0.0001,
    )

    assert result["filled"] is False
    assert result["reason"] == "slippage_exceeded"


def test_rejects_negative_fee_rate():
    scanner = OrderBookDepthAwareTriangleScanner(
        FakeOrderBookProvider()
    )

    with pytest.raises(ValueError, match="fee_rate must be non-negative"):
        scanner.scan_route(
            route=valid_route(),
            starting_value=100.0,
            fee_rate=-0.001,
            max_slippage_percent=1.0,
        )


def test_rejects_non_positive_starting_value():
    scanner = OrderBookDepthAwareTriangleScanner(
        FakeOrderBookProvider()
    )

    with pytest.raises(ValueError, match="starting_value must be positive"):
        scanner.scan_route(
            route=valid_route(),
            starting_value=0,
            fee_rate=0.004,
            max_slippage_percent=1.0,
        )
