from core.live_market_route_work_queue import (
    LiveMarketRouteWorkQueue,
)
from core.route_dependency_registry import (
    RouteDependencyRegistry,
)
from core.shared_live_market_data_cache import (
    SharedLiveMarketDataCache,
)
from core.queued_cross_exchange_shared_cache_route_worker import (
    QueuedCrossExchangeSharedCacheRouteWorker,
)


def snapshot(
    exchange_id,
    bid,
    ask,
):
    return {
        "exchange_id": exchange_id,
        "symbol": "ADA/USDT",
        "sequence": 1,
        "timestamp": 1.0,
        "bid": bid,
        "ask": ask,
        "bids": [[bid, 100000.0]],
        "asks": [[ask, 100000.0]],
    }


def route():
    return {
        "route_id": "K-B-ADA",
        "route_type": "cross_exchange",
        "exchange_id": "kucoin",
        "source_exchange": "kucoin",
        "destination_exchange": "bitget",
        "symbol": "ADA/USDT",
        "starting_value": 100.0,
        "source_fee_rate": 0.001,
        "destination_fee_rate": 0.001,
        "legs": [
            {
                "exchange_id": "kucoin",
                "symbol": "ADA/USDT",
                "side": "buy",
            },
            {
                "exchange_id": "bitget",
                "symbol": "ADA/USDT",
                "side": "sell",
            },
        ],
    }


def test_queue_worker_evaluates_cross_exchange_route():
    registry = RouteDependencyRegistry()
    registry.register(route())

    cache = SharedLiveMarketDataCache()

    cache.update(
        snapshot(
            "kucoin",
            0.499,
            0.500,
        )
    )

    cache.update(
        snapshot(
            "bitget",
            0.510,
            0.511,
        )
    )

    queue = LiveMarketRouteWorkQueue(
        max_queue_size=100
    )

    queue.enqueue({
        "request_id": "REQ-1",
        "route_id": "K-B-ADA",
        "exchange_id": "bitget",
        "symbol": "ADA/USDT",
        "sequence": 1,
        "priority": 1.0,
    })

    worker = (
        QueuedCrossExchangeSharedCacheRouteWorker(
            work_queue=queue,
            market_cache=cache,
            route_registry=registry,
        )
    )

    result = worker.process_next()

    assert result["processed"] is True
    assert result["filled"] is True
    assert result["net_profit"] > 0

    assert result[
        "trigger_exchange_id"
    ] == "bitget"

    assert result["paper_only"] is True
    assert (
        result["live_order_submitted"]
        is False
    )


def test_empty_queue_returns_none():
    worker = (
        QueuedCrossExchangeSharedCacheRouteWorker(
            work_queue=(
                LiveMarketRouteWorkQueue(
                    max_queue_size=10
                )
            ),
            market_cache=(
                SharedLiveMarketDataCache()
            ),
            route_registry=(
                RouteDependencyRegistry()
            ),
        )
    )

    assert worker.process_next() is None
