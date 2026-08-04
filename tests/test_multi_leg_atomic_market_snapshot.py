import pytest

from exchanges.multi_leg_atomic_market_snapshot import (
    MultiLegAtomicMarketSnapshot,
)


class FakeSnapshotEngine:
    def __init__(self):
        self.sequence = 0

    def snapshot(self, symbol, limit=None):
        self.sequence += 1
        return {
            "symbol": symbol,
            "bids": [[100.0, 2.0]],
            "asks": [[101.0, 2.0]],
            "best_bid": 100.0,
            "best_ask": 101.0,
            "timestamp": 1000 + self.sequence,
            "datetime": None,
        }


@pytest.fixture
def coordinator():
    return MultiLegAtomicMarketSnapshot(FakeSnapshotEngine())


def valid_route():
    return {
        "route_id": "ROUTE-001",
        "legs": [
            {"symbol": "BTC/USDT"},
            {"symbol": "ETH/BTC"},
            {"symbol": "ETH/USDT"},
        ],
    }


def test_captures_snapshot_for_every_route_leg(coordinator):
    result = coordinator.capture(valid_route())

    assert result["route_id"] == "ROUTE-001"
    assert len(result["snapshots"]) == 3
    assert result["snapshots"][0]["symbol"] == "BTC/USDT"
    assert result["snapshots"][1]["symbol"] == "ETH/BTC"
    assert result["snapshots"][2]["symbol"] == "ETH/USDT"


def test_reports_snapshot_time_spread(coordinator):
    result = coordinator.capture(valid_route())

    assert result["earliest_timestamp"] == 1001
    assert result["latest_timestamp"] == 1003
    assert result["snapshot_spread_ms"] == 2


def test_rejects_snapshot_when_time_spread_exceeds_limit():
    coordinator = MultiLegAtomicMarketSnapshot(
        FakeSnapshotEngine(),
        max_spread_ms=1,
    )

    with pytest.raises(ValueError, match="snapshot spread exceeded"):
        coordinator.capture(valid_route())


def test_missing_route_is_rejected(coordinator):
    with pytest.raises(ValueError, match="route is required"):
        coordinator.capture(None)


def test_missing_legs_are_rejected(coordinator):
    route = {"route_id": "ROUTE-001"}

    with pytest.raises(ValueError, match="legs are required"):
        coordinator.capture(route)
