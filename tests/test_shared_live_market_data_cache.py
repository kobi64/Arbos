import pytest

from core.shared_live_market_data_cache import (
    SharedLiveMarketDataCache,
)


class FakeFreshnessGuard:
    def __init__(self):
        self.calls = []

    def evaluate(
        self,
        symbol,
        timestamp,
    ):
        self.calls.append(
            (
                symbol,
                timestamp,
            )
        )

        return {
            "symbol": symbol,
            "fresh": (
                float(timestamp) >= 1000.0
            ),
            "reason": (
                None
                if float(timestamp) >= 1000.0
                else "market_data_stale"
            ),
            "age_seconds": 0.0,
            "max_age_seconds": 5.0,
        }


def snapshot(
    sequence,
    timestamp,
    bid=100.0,
    ask=101.0,
):
    return {
        "exchange_id": "kucoin",
        "symbol": "BTC/USDT",
        "sequence": sequence,
        "timestamp": timestamp,
        "bid": bid,
        "ask": ask,
        "bids": [
            [bid, 1.0],
        ],
        "asks": [
            [ask, 1.0],
        ],
    }


def test_stores_and_reads_latest_market_snapshot():
    cache = SharedLiveMarketDataCache()

    result = cache.update(
        snapshot(
            sequence=100,
            timestamp=1000.0,
        )
    )

    assert result["updated"] is True

    stored = cache.get(
        exchange_id="kucoin",
        symbol="BTC/USDT",
    )

    assert stored["sequence"] == 100
    assert stored["bid"] == 100.0
    assert stored["ask"] == 101.0


def test_newer_sequence_replaces_existing_snapshot():
    cache = SharedLiveMarketDataCache()

    cache.update(
        snapshot(
            sequence=100,
            timestamp=1000.0,
        )
    )

    cache.update(
        snapshot(
            sequence=101,
            timestamp=1001.0,
            bid=102.0,
            ask=103.0,
        )
    )

    stored = cache.get(
        exchange_id="kucoin",
        symbol="BTC/USDT",
    )

    assert stored["sequence"] == 101
    assert stored["bid"] == 102.0


def test_older_sequence_is_rejected():
    cache = SharedLiveMarketDataCache()

    cache.update(
        snapshot(
            sequence=105,
            timestamp=1005.0,
        )
    )

    result = cache.update(
        snapshot(
            sequence=104,
            timestamp=1006.0,
        )
    )

    assert result["updated"] is False
    assert result["reason"] == (
        "stale_market_sequence"
    )

    stored = cache.get(
        exchange_id="kucoin",
        symbol="BTC/USDT",
    )

    assert stored["sequence"] == 105


def test_duplicate_sequence_is_rejected():
    cache = SharedLiveMarketDataCache()

    cache.update(
        snapshot(
            sequence=100,
            timestamp=1000.0,
        )
    )

    result = cache.update(
        snapshot(
            sequence=100,
            timestamp=1001.0,
        )
    )

    assert result["updated"] is False
    assert result["reason"] == (
        "duplicate_market_sequence"
    )


def test_exchange_and_symbol_are_normalized():
    cache = SharedLiveMarketDataCache()

    data = snapshot(
        sequence=1,
        timestamp=1000.0,
    )

    data["exchange_id"] = " KUCOIN "
    data["symbol"] = "btc/usdt"

    cache.update(data)

    stored = cache.get(
        exchange_id="kucoin",
        symbol="BTC/USDT",
    )

    assert stored["exchange_id"] == "kucoin"
    assert stored["symbol"] == "BTC/USDT"


def test_get_returns_copy_safe_snapshot():
    cache = SharedLiveMarketDataCache()

    cache.update(
        snapshot(
            sequence=100,
            timestamp=1000.0,
        )
    )

    first = cache.get(
        exchange_id="kucoin",
        symbol="BTC/USDT",
    )

    first["bid"] = 999999.0
    first["bids"][0][0] = 999999.0

    second = cache.get(
        exchange_id="kucoin",
        symbol="BTC/USDT",
    )

    assert second["bid"] == 100.0
    assert second["bids"][0][0] == 100.0


def test_unknown_market_returns_none():
    cache = SharedLiveMarketDataCache()

    assert cache.get(
        exchange_id="gate",
        symbol="SOL/USDT",
    ) is None


def test_freshness_guard_is_used_when_supplied():
    guard = FakeFreshnessGuard()

    cache = SharedLiveMarketDataCache(
        freshness_guard=guard
    )

    cache.update(
        snapshot(
            sequence=100,
            timestamp=1000.0,
        )
    )

    result = cache.get_with_freshness(
        exchange_id="kucoin",
        symbol="BTC/USDT",
    )

    assert result["snapshot"][
        "sequence"
    ] == 100

    assert result["freshness"][
        "fresh"
    ] is True

    assert guard.calls == [
        (
            "BTC/USDT",
            1000.0,
        ),
    ]


def test_stale_snapshot_is_reported_not_deleted():
    guard = FakeFreshnessGuard()

    cache = SharedLiveMarketDataCache(
        freshness_guard=guard
    )

    cache.update(
        snapshot(
            sequence=99,
            timestamp=999.0,
        )
    )

    result = cache.get_with_freshness(
        exchange_id="kucoin",
        symbol="BTC/USDT",
    )

    assert result["snapshot"] is not None
    assert result["freshness"][
        "fresh"
    ] is False

    assert result["freshness"][
        "reason"
    ] == "market_data_stale"


def test_market_count_tracks_distinct_exchange_symbols():
    cache = SharedLiveMarketDataCache()

    first = snapshot(
        sequence=1,
        timestamp=1000.0,
    )

    second = snapshot(
        sequence=1,
        timestamp=1000.0,
    )

    second["exchange_id"] = "gate"

    cache.update(first)
    cache.update(second)

    assert cache.market_count() == 2


def test_exchange_id_is_required():
    cache = SharedLiveMarketDataCache()

    data = snapshot(
        sequence=1,
        timestamp=1000.0,
    )

    data.pop("exchange_id")

    with pytest.raises(
        ValueError,
        match="exchange_id is required",
    ):
        cache.update(data)


def test_symbol_is_required():
    cache = SharedLiveMarketDataCache()

    data = snapshot(
        sequence=1,
        timestamp=1000.0,
    )

    data.pop("symbol")

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        cache.update(data)


def test_timestamp_is_required():
    cache = SharedLiveMarketDataCache()

    data = snapshot(
        sequence=1,
        timestamp=1000.0,
    )

    data.pop("timestamp")

    with pytest.raises(
        ValueError,
        match="timestamp is required",
    ):
        cache.update(data)
