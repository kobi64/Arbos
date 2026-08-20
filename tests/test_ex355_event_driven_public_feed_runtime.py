import asyncio

import pytest

from core.event_driven_public_feed_runtime import (
    EventDrivenPublicFeedRuntime,
)
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

    def process_next(self):
        item = self._queue.dequeue()

        if item is None:
            return None

        return {
            "processed": True,
            "route_id": item["route_id"],
            "paper_only": True,
            "live_order_submitted": False,
        }


class FakeExchange:
    def __init__(self, exchange_id):
        self.id = exchange_id
        self.counter = 0
        self.closed = False

    async def watch_order_book(
        self,
        symbol,
        limit=None,
    ):
        self.counter += 1

        await asyncio.sleep(0)

        return {
            "symbol": symbol,
            "bids": [
                [100.0, 10.0],
            ],
            "asks": [
                [101.0, 10.0],
            ],
            "timestamp": (
                self.counter * 1000
            ),
            "nonce": self.counter,
        }

    async def close(self):
        self.closed = True


def route(
    route_id,
    exchange_id,
    symbol,
):
    return {
        "route_id": route_id,
        "exchange_id": exchange_id,
        "starting_value": 100.0,
        "fee_rate": 0.001,
        "max_slippage_percent": 0.5,
        "legs": [
            {
                "symbol": symbol,
                "side": "buy",
            },
        ],
    }


def test_runtime_builds_one_manager_per_exchange():
    engine = EventDrivenSharedCacheScanEngine(
        worker_factory=FakeWorker,
        worker_count=4,
    )

    runtime = EventDrivenPublicFeedRuntime(
        engine=engine,
        exchanges={
            "kucoin": FakeExchange("kucoin"),
            "bitget": FakeExchange("bitget"),
            "htx": FakeExchange("htx"),
        },
        exchange_symbols={
            "kucoin": ["BTC/USDT"],
            "bitget": ["ETH/USDT"],
            "htx": ["DOGE/USDT"],
        },
    )

    assert sorted(
        runtime.managers
    ) == [
        "bitget",
        "htx",
        "kucoin",
    ]

    status = runtime.status()

    assert status[
        "exchange_count"
    ] == 3

    assert status[
        "symbol_count"
    ] == 3

    assert status["paper_only"] is True
    assert (
        status["live_order_submitted"]
        is False
    )


def test_runtime_feeds_shared_engine():
    engine = EventDrivenSharedCacheScanEngine(
        worker_factory=FakeWorker,
        worker_count=4,
    )

    engine.register_route(
        route(
            "R-BTC",
            "kucoin",
            "BTC/USDT",
        )
    )

    exchange = FakeExchange(
        "kucoin"
    )

    runtime = EventDrivenPublicFeedRuntime(
        engine=engine,
        exchanges={
            "kucoin": exchange,
        },
        exchange_symbols={
            "kucoin": [
                "BTC/USDT",
            ],
        },
    )

    async def exercise():
        manager = (
            runtime.managers[
                "kucoin"
            ]
        )

        result = await manager.run_cycles(
            cycles_per_symbol=1
        )

        assert result[
            "completed_updates"
        ] == 1

    asyncio.run(exercise())

    assert (
        engine.work_queue
        .pending_count()
        == 1
    )

    processing = (
        runtime.process_pending()
    )

    assert processing[
        "processed_count"
    ] == 1

    assert processing[
        "live_order_submitted"
    ] is False


def test_symbols_are_normalized_and_deduplicated():
    engine = EventDrivenSharedCacheScanEngine(
        worker_factory=FakeWorker,
    )

    runtime = EventDrivenPublicFeedRuntime(
        engine=engine,
        exchanges={
            "kucoin": FakeExchange(
                "kucoin"
            ),
        },
        exchange_symbols={
            "kucoin": [
                " btc/usdt ",
                "BTC/USDT",
                "",
                "eth/usdt",
            ],
        },
    )

    assert (
        runtime.managers[
            "kucoin"
        ].symbols
        == [
            "BTC/USDT",
            "ETH/USDT",
        ]
    )


def test_required_dependencies_are_validated():
    engine = EventDrivenSharedCacheScanEngine(
        worker_factory=FakeWorker,
    )

    with pytest.raises(
        ValueError,
        match="engine is required",
    ):
        EventDrivenPublicFeedRuntime(
            engine=None,
            exchanges={
                "kucoin": (
                    FakeExchange(
                        "kucoin"
                    )
                ),
            },
            exchange_symbols={
                "kucoin": [
                    "BTC/USDT",
                ],
            },
        )

    with pytest.raises(
        ValueError,
        match="exchanges are required",
    ):
        EventDrivenPublicFeedRuntime(
            engine=engine,
            exchanges={},
            exchange_symbols={
                "kucoin": [
                    "BTC/USDT",
                ],
            },
        )

    with pytest.raises(
        ValueError,
        match=(
            "exchange_symbols "
            "are required"
        ),
    ):
        EventDrivenPublicFeedRuntime(
            engine=engine,
            exchanges={
                "kucoin": (
                    FakeExchange(
                        "kucoin"
                    )
                ),
            },
            exchange_symbols={},
        )


def test_runtime_remains_paper_safe():
    engine = EventDrivenSharedCacheScanEngine(
        worker_factory=FakeWorker,
    )

    runtime = EventDrivenPublicFeedRuntime(
        engine=engine,
        exchanges={
            "kucoin": FakeExchange(
                "kucoin"
            ),
        },
        exchange_symbols={
            "kucoin": [
                "BTC/USDT",
            ],
        },
    )

    status = runtime.status()

    assert status["paper_only"] is True
    assert (
        status["live_order_submitted"]
        is False
    )


def test_runtime_injects_exchange_backoff_policy_into_manager():
    class Engine:
        work_queue = object()
        route_registry = object()
        market_cache = object()

    class Exchange:
        id = "kucoin"

    class BackoffPolicy:
        pass

    policy = BackoffPolicy()

    runtime = EventDrivenPublicFeedRuntime(
        engine=Engine(),
        exchanges={
            "kucoin": Exchange(),
        },
        exchange_symbols={
            "kucoin": [
                "BTC/USDT",
            ],
        },
        backoff_policies={
            "kucoin": policy,
        },
    )

    manager = runtime.managers[
        "kucoin"
    ]

    assert manager._backoff_policy is policy
