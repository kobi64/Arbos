import threading
import time

from core.event_driven_shared_cache_scan_engine import (
    EventDrivenSharedCacheScanEngine,
)


class FakeWorker:
    def __init__(
        self,
        work_queue,
        market_cache,
        route_registry,
    ):
        self._queue = work_queue
        self._cache = market_cache
        self._registry = route_registry

    def process_next(self):
        item = self._queue.dequeue()

        if item is None:
            return None

        route = self._registry.get(
            item["route_id"]
        )

        return {
            "processed": True,
            "route_id": item["route_id"],
            "route": route,
            "paper_only": True,
            "live_order_submitted": False,
        }


class SlowWorker:
    active = 0
    maximum_active = 0
    lock = threading.Lock()

    def __init__(
        self,
        work_queue,
        market_cache,
        route_registry,
    ):
        self._queue = work_queue

    def process_next(self):
        item = self._queue.dequeue()

        if item is None:
            return None

        with self.lock:
            type(self).active += 1
            type(self).maximum_active = max(
                type(self).maximum_active,
                type(self).active,
            )

        try:
            time.sleep(0.02)

            return {
                "processed": True,
                "route_id": item["route_id"],
                "paper_only": True,
                "live_order_submitted": False,
            }

        finally:
            with self.lock:
                type(self).active -= 1


def route(
    route_id,
    coin,
):
    return {
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
    }


def snapshot(
    symbol,
    sequence,
):
    return {
        "exchange_id": "kucoin",
        "symbol": symbol,
        "sequence": sequence,
        "timestamp": time.time(),
        "bid": 100.0,
        "ask": 101.0,
    }


def test_market_update_queues_only_dependent_routes():
    engine = EventDrivenSharedCacheScanEngine(
        worker_factory=FakeWorker,
        worker_count=2,
    )

    engine.register_route(
        route("ETH", "ETH")
    )

    engine.register_route(
        route("SOL", "SOL")
    )

    result = engine.publish(
        snapshot(
            "ETH/USDT",
            1,
        )
    )

    assert result[
        "dispatch"
    ][
        "affected_route_ids"
    ] == [
        "ETH"
    ]

    assert engine.work_queue.pending_count() == 1


def test_shared_market_update_can_wake_many_routes():
    engine = EventDrivenSharedCacheScanEngine(
        worker_factory=FakeWorker,
        worker_count=4,
    )

    for index in range(100):
        engine.register_route(
            route(
                f"R{index}",
                f"C{index}",
            )
        )

    result = engine.publish(
        snapshot(
            "BTC/USDT",
            10,
        )
    )

    assert result[
        "dispatch"
    ][
        "affected_route_count"
    ] == 100

    assert (
        engine.work_queue.pending_count()
        == 100
    )


def test_newer_updates_coalesce_route_work():
    engine = EventDrivenSharedCacheScanEngine(
        worker_factory=FakeWorker,
        worker_count=2,
    )

    engine.register_route(
        route("ETH", "ETH")
    )

    engine.publish(
        snapshot(
            "ETH/USDT",
            100,
        )
    )

    engine.publish(
        snapshot(
            "ETH/USDT",
            101,
        )
    )

    engine.publish(
        snapshot(
            "ETH/USDT",
            102,
        )
    )

    assert (
        engine.work_queue.pending_count()
        == 1
    )

    item = engine.work_queue.dequeue()

    assert item["sequence"] == 102


def test_duplicate_snapshot_does_not_create_work():
    engine = EventDrivenSharedCacheScanEngine(
        worker_factory=FakeWorker,
        worker_count=2,
    )

    engine.register_route(
        route("ETH", "ETH")
    )

    engine.publish(
        snapshot(
            "ETH/USDT",
            200,
        )
    )

    engine.work_queue.dequeue()

    result = engine.publish(
        snapshot(
            "ETH/USDT",
            200,
        )
    )

    assert result["updated"] is False
    assert result["dispatched"] is False
    assert (
        engine.work_queue.pending_count()
        == 0
    )


def test_parallel_pool_is_actually_concurrent():
    SlowWorker.active = 0
    SlowWorker.maximum_active = 0

    engine = EventDrivenSharedCacheScanEngine(
        worker_factory=SlowWorker,
        worker_count=8,
    )

    for index in range(40):
        engine.register_route(
            route(
                f"R{index}",
                f"C{index}",
            )
        )

    engine.publish(
        snapshot(
            "BTC/USDT",
            300,
        )
    )

    result = engine.process_pending()

    assert result[
        "processed_count"
    ] == 40

    assert (
        SlowWorker.maximum_active
        > 1
    )

    assert result["paper_only"] is True
    assert (
        result["live_order_submitted"]
        is False
    )


def test_batch_processes_registered_route_once_after_coalescing():
    engine = EventDrivenSharedCacheScanEngine(
        worker_factory=FakeWorker,
        worker_count=4,
    )

    engine.register_route(
        route("ETH", "ETH")
    )

    result = engine.run_batch([
        snapshot(
            "ETH/USDT",
            400,
        ),
        snapshot(
            "ETH/USDT",
            401,
        ),
        snapshot(
            "ETH/USDT",
            402,
        ),
    ])

    assert result[
        "processing"
    ][
        "processed_count"
    ] == 1

    assert (
        result["registered_route_count"]
        == 1
    )

    assert result["paper_only"] is True
    assert (
        result["live_order_submitted"]
        is False
    )


def test_process_pending_can_be_bounded():
    engine = EventDrivenSharedCacheScanEngine(
        worker_factory=FakeWorker,
        worker_count=4,
    )

    for index in range(20):
        engine.register_route(
            route(
                f"R-B-{index}",
                f"C-B-{index}",
            )
        )

    engine.publish(
        snapshot(
            "BTC/USDT",
            500,
        )
    )

    result = engine.process_pending(
        max_items=7
    )

    assert result[
        "processed_count"
    ] == 7

    assert (
        engine.work_queue
        .pending_count()
        == 13
    )
