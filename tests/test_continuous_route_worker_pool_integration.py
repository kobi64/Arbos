from core.continuous_route_worker_pool import (
    ContinuousRouteWorkerPool,
)
from core.live_market_route_work_queue import (
    LiveMarketRouteWorkQueue,
)
from core.route_dependency_registry import (
    RouteDependencyRegistry,
)
from core.shared_cache_route_worker import (
    SharedCacheRouteWorker,
)
from core.shared_live_market_data_cache import (
    SharedLiveMarketDataCache,
)


def order_book_snapshot(
    exchange_id,
    symbol,
    sequence,
    bid,
    ask,
):
    return {
        "exchange_id": exchange_id,
        "symbol": symbol,
        "sequence": sequence,
        "timestamp": float(sequence),
        "bids": [
            [bid, 10000.0],
        ],
        "asks": [
            [ask, 10000.0],
        ],
    }


def register_route(
    registry,
    route_id,
    coin,
):
    registry.register({
        "route_id": route_id,
        "exchange_id": "kucoin",
        "starting_value": 100.0,
        "fee_rate": 0.001,
        "max_slippage_percent": 0.5,
        "legs": [
            {
                "symbol": f"{coin}/USDT",
                "side": "buy",
            },
            {
                "symbol": f"{coin}/BTC",
                "side": "sell",
            },
            {
                "symbol": "BTC/USDT",
                "side": "sell",
            },
        ],
    })


def test_real_workers_drain_real_queue_from_shared_cache():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=100
    )

    registry = RouteDependencyRegistry()

    register_route(
        registry,
        "R-ETH",
        "ETH",
    )

    register_route(
        registry,
        "R-SOL",
        "SOL",
    )

    cache = SharedLiveMarketDataCache()

    snapshots = [
        order_book_snapshot(
            "kucoin",
            "ETH/USDT",
            1,
            1999.0,
            2000.0,
        ),
        order_book_snapshot(
            "kucoin",
            "ETH/BTC",
            1,
            0.04,
            0.0401,
        ),
        order_book_snapshot(
            "kucoin",
            "SOL/USDT",
            1,
            99.9,
            100.0,
        ),
        order_book_snapshot(
            "kucoin",
            "SOL/BTC",
            1,
            0.002,
            0.00201,
        ),
        order_book_snapshot(
            "kucoin",
            "BTC/USDT",
            1,
            50000.0,
            50010.0,
        ),
    ]

    for snapshot in snapshots:
        cache.update(snapshot)

    queue.enqueue({
        "request_id": "REQ-ETH",
        "route_id": "R-ETH",
        "sequence": 1,
        "priority": 1.0,
    })

    queue.enqueue({
        "request_id": "REQ-SOL",
        "route_id": "R-SOL",
        "sequence": 1,
        "priority": 1.0,
    })

    pool = ContinuousRouteWorkerPool(
        worker_count=2,
        work_queue=queue,
        market_cache=cache,
        route_registry=registry,
        worker_factory=SharedCacheRouteWorker,
    )

    result = pool.run_until_empty()

    assert result["processed_count"] == 2
    assert result["remaining_count"] == 0

    route_ids = {
        item["route_id"]
        for item in result["results"]
    }

    assert route_ids == {
        "R-ETH",
        "R-SOL",
    }

    assert all(
        item["processed"] is True
        for item in result["results"]
    )

    assert all(
        item["paper_only"] is True
        for item in result["results"]
    )

    assert all(
        item["live_order_submitted"]
        is False
        for item in result["results"]
    )
