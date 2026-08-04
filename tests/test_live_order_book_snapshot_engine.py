import pytest

from exchanges.live_order_book_snapshot_engine import (
    LiveOrderBookSnapshotEngine,
)


class FakeExchange:
    def fetch_order_book(self, symbol, limit=None):
        return {
            "symbol": symbol,
            "bids": [[100.0, 2.0], [99.0, 3.0]],
            "asks": [[101.0, 1.5], [102.0, 4.0]],
            "timestamp": 1234567890,
            "datetime": "2026-08-04T16:00:00Z",
        }


@pytest.fixture
def engine():
    return LiveOrderBookSnapshotEngine(FakeExchange())


def test_fetches_order_book_snapshot(engine):
    result = engine.snapshot("BTC/USDT")

    assert result["symbol"] == "BTC/USDT"
    assert result["best_bid"] == 100.0
    assert result["best_ask"] == 101.0


def test_preserves_timestamp_and_datetime(engine):
    result = engine.snapshot("BTC/USDT")

    assert result["timestamp"] == 1234567890
    assert result["datetime"] == "2026-08-04T16:00:00Z"


def test_returns_full_depth(engine):
    result = engine.snapshot("BTC/USDT")

    assert len(result["bids"]) == 2
    assert len(result["asks"]) == 2
    assert result["bids"][0] == [100.0, 2.0]
    assert result["asks"][0] == [101.0, 1.5]


def test_rejects_missing_symbol(engine):
    with pytest.raises(ValueError, match="symbol is required"):
        engine.snapshot("")


def test_rejects_none_symbol(engine):
    with pytest.raises(ValueError, match="symbol is required"):
        engine.snapshot(None)


class EmptyOrderBookExchange:
    def fetch_order_book(self, symbol, limit=None):
        return {
            "symbol": symbol,
            "bids": [],
            "asks": [],
            "timestamp": 1234567890,
            "datetime": "2026-08-04T16:00:00Z",
        }


def test_rejects_empty_order_book():
    engine = LiveOrderBookSnapshotEngine(EmptyOrderBookExchange())

    with pytest.raises(ValueError, match="order book unavailable"):
        engine.snapshot("BTC/USDT")
