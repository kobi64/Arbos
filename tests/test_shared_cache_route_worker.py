import pytest

from core.shared_cache_route_worker import (
    SharedCacheRouteWorker,
)


class FakeWorkQueue:
    def __init__(self, items=None):
        self.items = list(items or [])

    def dequeue(self):
        if not self.items:
            return None

        return self.items.pop(0)


class FakeCache:
    def __init__(self):
        self.snapshots = {}

    def put(
        self,
        exchange_id,
        symbol,
        snapshot,
        fresh=True,
    ):
        self.snapshots[
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
        return self.snapshots.get(
            (
                exchange_id.lower(),
                symbol.upper(),
            ),
            {
                "snapshot": None,
                "freshness": None,
            },
        )


def order_book(
    bid,
    ask,
    quantity=10000.0,
):
    return {
        "bids": [
            [bid, quantity],
        ],
        "asks": [
            [ask, quantity],
        ],
    }


def route_registry():
    return {
        "R-ETH-BTC": {
            "route_id": "R-ETH-BTC",
            "exchange_id": "kucoin",
            "starting_value": 100.0,
            "fee_rate": 0.001,
            "max_slippage_percent": 0.5,
            "legs": [
                {
                    "symbol": "ETH/USDT",
                    "side": "buy",
                },
                {
                    "symbol": "ETH/BTC",
                    "side": "sell",
                },
                {
                    "symbol": "BTC/USDT",
                    "side": "sell",
                },
            ],
        },
    }


def populated_cache():
    cache = FakeCache()

    cache.put(
        "kucoin",
        "ETH/USDT",
        order_book(
            bid=1999.0,
            ask=2000.0,
        ),
    )

    cache.put(
        "kucoin",
        "ETH/BTC",
        order_book(
            bid=0.04,
            ask=0.0401,
        ),
    )

    cache.put(
        "kucoin",
        "BTC/USDT",
        order_book(
            bid=50000.0,
            ask=50010.0,
        ),
    )

    return cache


def test_worker_evaluates_route_entirely_from_shared_cache():
    queue = FakeWorkQueue([
        {
            "request_id": "REQ-1",
            "route_id": "R-ETH-BTC",
            "sequence": 100,
            "priority": 5.0,
        },
    ])

    worker = SharedCacheRouteWorker(
        work_queue=queue,
        market_cache=populated_cache(),
        route_registry=route_registry(),
    )

    result = worker.process_next()

    assert result["processed"] is True
    assert result["route_id"] == "R-ETH-BTC"

    assert result["filled"] is True

    assert result["paper_only"] is True

    assert (
        result["live_order_submitted"]
        is False
    )

    assert len(
        result["legs"]
    ) == 3


def test_missing_cached_market_rejects_route_without_api_call():
    cache = populated_cache()

    cache.snapshots.pop(
        (
            "kucoin",
            "ETH/BTC",
        )
    )

    worker = SharedCacheRouteWorker(
        work_queue=FakeWorkQueue([
            {
                "request_id": "REQ-2",
                "route_id": "R-ETH-BTC",
                "sequence": 101,
            },
        ]),
        market_cache=cache,
        route_registry=route_registry(),
    )

    result = worker.process_next()

    assert result["processed"] is True
    assert result["filled"] is False

    assert result["reason"] == (
        "market_snapshot_unavailable"
    )

    assert result[
        "missing_symbol"
    ] == "ETH/BTC"


def test_stale_cached_market_rejects_route():
    cache = populated_cache()

    cache.put(
        "kucoin",
        "BTC/USDT",
        order_book(
            bid=50000.0,
            ask=50010.0,
        ),
        fresh=False,
    )

    worker = SharedCacheRouteWorker(
        work_queue=FakeWorkQueue([
            {
                "request_id": "REQ-3",
                "route_id": "R-ETH-BTC",
                "sequence": 102,
            },
        ]),
        market_cache=cache,
        route_registry=route_registry(),
    )

    result = worker.process_next()

    assert result["filled"] is False

    assert result["reason"] == (
        "market_data_stale"
    )

    assert result[
        "stale_symbol"
    ] == "BTC/USDT"


def test_unknown_route_is_rejected_cleanly():
    worker = SharedCacheRouteWorker(
        work_queue=FakeWorkQueue([
            {
                "request_id": "REQ-4",
                "route_id": "UNKNOWN",
                "sequence": 103,
            },
        ]),
        market_cache=populated_cache(),
        route_registry=route_registry(),
    )

    result = worker.process_next()

    assert result["processed"] is True
    assert result["filled"] is False

    assert result["reason"] == (
        "route_not_registered"
    )


def test_empty_queue_returns_none():
    worker = SharedCacheRouteWorker(
        work_queue=FakeWorkQueue(),
        market_cache=populated_cache(),
        route_registry=route_registry(),
    )

    assert worker.process_next() is None


def test_worker_reads_latest_cached_state_each_time():
    cache = populated_cache()

    queue = FakeWorkQueue([
        {
            "request_id": "REQ-5",
            "route_id": "R-ETH-BTC",
            "sequence": 104,
        },
        {
            "request_id": "REQ-6",
            "route_id": "R-ETH-BTC",
            "sequence": 105,
        },
    ])

    worker = SharedCacheRouteWorker(
        work_queue=queue,
        market_cache=cache,
        route_registry=route_registry(),
    )

    first = worker.process_next()

    cache.put(
        "kucoin",
        "BTC/USDT",
        order_book(
            bid=51000.0,
            ask=51010.0,
        ),
    )

    second = worker.process_next()

    assert (
        first["net_final_value"]
        != second["net_final_value"]
    )


def test_missing_dependencies_are_rejected():
    with pytest.raises(
        ValueError,
        match="work_queue is required",
    ):
        SharedCacheRouteWorker(
            work_queue=None,
            market_cache=populated_cache(),
            route_registry=route_registry(),
        )

    with pytest.raises(
        ValueError,
        match="market_cache is required",
    ):
        SharedCacheRouteWorker(
            work_queue=FakeWorkQueue(),
            market_cache=None,
            route_registry=route_registry(),
        )

    with pytest.raises(
        ValueError,
        match="route_registry is required",
    ):
        SharedCacheRouteWorker(
            work_queue=FakeWorkQueue(),
            market_cache=populated_cache(),
            route_registry=None,
        )
