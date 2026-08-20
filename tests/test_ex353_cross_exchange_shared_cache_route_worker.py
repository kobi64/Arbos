import pytest

from core.cross_exchange_shared_cache_route_worker import (
    CrossExchangeSharedCacheRouteWorker,
)


class FakeCache:
    def __init__(self):
        self.data = {}

    def put(
        self,
        exchange_id,
        symbol,
        snapshot,
        fresh=True,
    ):
        self.data[
            (
                exchange_id.lower(),
                symbol.upper(),
            )
        ] = {
            "snapshot": snapshot,
            "freshness": {
                "fresh": fresh,
                "reason": (
                    None
                    if fresh
                    else "market_data_stale"
                ),
            },
        }

    def get_with_freshness(
        self,
        exchange_id,
        symbol,
    ):
        return self.data.get(
            (
                exchange_id.lower(),
                symbol.upper(),
            ),
            {
                "snapshot": None,
                "freshness": None,
            },
        )


def book(
    bid,
    ask,
):
    return {
        "bids": [
            [bid, 100000.0],
        ],
        "asks": [
            [ask, 100000.0],
        ],
    }


def registry():
    return {
        "KUCOIN-BITGET-ADA": {
            "route_id": (
                "KUCOIN-BITGET-ADA"
            ),
            "route_type": (
                "cross_exchange"
            ),
            "source_exchange": (
                "kucoin"
            ),
            "destination_exchange": (
                "bitget"
            ),
            "symbol": "ADA/USDT",
            "starting_value": 100.0,
            "source_fee_rate": 0.001,
            "destination_fee_rate": 0.001,
        },
    }


def populated_cache():
    cache = FakeCache()

    cache.put(
        "kucoin",
        "ADA/USDT",
        book(
            bid=0.499,
            ask=0.500,
        ),
    )

    cache.put(
        "bitget",
        "ADA/USDT",
        book(
            bid=0.510,
            ask=0.511,
        ),
    )

    return cache


def test_cross_exchange_route_uses_cache_only():
    worker = (
        CrossExchangeSharedCacheRouteWorker(
            market_cache=(
                populated_cache()
            ),
            route_registry=registry(),
        )
    )

    result = worker.evaluate(
        "KUCOIN-BITGET-ADA"
    )

    assert result["processed"] is True
    assert result["filled"] is True

    assert (
        result["source_exchange"]
        == "kucoin"
    )

    assert (
        result[
            "destination_exchange"
        ]
        == "bitget"
    )

    assert result["source_ask"] == 0.5
    assert (
        result["destination_bid"]
        == 0.51
    )

    assert (
        result["net_profit"]
        > 0
    )

    assert result["paper_only"] is True

    assert (
        result["live_order_submitted"]
        is False
    )


def test_missing_source_snapshot_rejects():
    cache = populated_cache()

    cache.data.pop(
        (
            "kucoin",
            "ADA/USDT",
        )
    )

    worker = (
        CrossExchangeSharedCacheRouteWorker(
            market_cache=cache,
            route_registry=registry(),
        )
    )

    result = worker.evaluate(
        "KUCOIN-BITGET-ADA"
    )

    assert result["filled"] is False

    assert result["reason"] == (
        "market_snapshot_unavailable"
    )


def test_stale_destination_rejects():
    cache = populated_cache()

    cache.put(
        "bitget",
        "ADA/USDT",
        book(
            bid=0.510,
            ask=0.511,
        ),
        fresh=False,
    )

    worker = (
        CrossExchangeSharedCacheRouteWorker(
            market_cache=cache,
            route_registry=registry(),
        )
    )

    result = worker.evaluate(
        "KUCOIN-BITGET-ADA"
    )

    assert result["filled"] is False

    assert result["reason"] == (
        "market_data_stale"
    )


def test_unknown_route_rejects():
    worker = (
        CrossExchangeSharedCacheRouteWorker(
            market_cache=(
                populated_cache()
            ),
            route_registry=registry(),
        )
    )

    result = worker.evaluate(
        "UNKNOWN"
    )

    assert result["filled"] is False

    assert result["reason"] == (
        "route_not_registered"
    )


def test_dependencies_required():
    with pytest.raises(
        ValueError,
        match="market_cache is required",
    ):
        CrossExchangeSharedCacheRouteWorker(
            market_cache=None,
            route_registry={},
        )

    with pytest.raises(
        ValueError,
        match="route_registry is required",
    ):
        CrossExchangeSharedCacheRouteWorker(
            market_cache=FakeCache(),
            route_registry=None,
        )
