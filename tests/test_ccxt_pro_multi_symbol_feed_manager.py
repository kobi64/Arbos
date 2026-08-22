from core.ccxt_pro_multi_symbol_feed_manager import (
    CCXTProMultiSymbolFeedManager,
)


class FakeFeed:
    pass


class FakeExchange:
    pass


def test_manager_normalizes_symbols():
    manager = CCXTProMultiSymbolFeedManager(
        feed=FakeFeed(),
        exchange=FakeExchange(),
        symbols=[
            " btc/usdt ",
            "ETH/USDT",
            "btc/usdt",
        ],
    )

    assert manager.symbols == [
        "BTC/USDT",
        "ETH/USDT",
    ]


def test_run_cycles_processes_multiple_symbols():
    import asyncio

    class RecordingFeed:
        def __init__(self):
            self.calls = []

        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            self.calls.append(symbol)

            await asyncio.sleep(0)

            return {
                "accepted": True,
                "symbol": symbol,
            }

    feed = RecordingFeed()

    manager = CCXTProMultiSymbolFeedManager(
        feed=feed,
        exchange=FakeExchange(),
        symbols=[
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
        ],
    )

    result = asyncio.run(
        manager.run_cycles(
            cycles_per_symbol=1
        )
    )

    assert result["completed_updates"] == 3

    assert set(feed.calls) == {
        "BTC/USDT",
        "ETH/USDT",
        "SOL/USDT",
    }

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_multiple_symbols_run_concurrently():
    import asyncio
    import time

    class SlowFeed:
        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            await asyncio.sleep(0.05)

            return {
                "accepted": True,
                "symbol": symbol,
            }

    manager = CCXTProMultiSymbolFeedManager(
        feed=SlowFeed(),
        exchange=FakeExchange(),
        symbols=[
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
        ],
    )

    started = time.perf_counter()

    result = asyncio.run(
        manager.run_cycles(
            cycles_per_symbol=1
        )
    )

    elapsed = (
        time.perf_counter()
        - started
    )

    assert result[
        "completed_updates"
    ] == 3

    assert elapsed < 0.11


def test_manager_can_start_and_stop_persistent_tasks():
    import asyncio

    class BlockingFeed:
        def __init__(self):
            self.calls = []

        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            self.calls.append(symbol)
            await asyncio.sleep(3600)

    class ClosingExchange:
        def __init__(self):
            self.closed = False

        async def close(self):
            self.closed = True

    feed = BlockingFeed()
    exchange = ClosingExchange()

    manager = CCXTProMultiSymbolFeedManager(
        feed=feed,
        exchange=exchange,
        symbols=[
            "BTC/USDT",
            "ETH/USDT",
        ],
    )

    async def exercise():
        result = await manager.start()

        await asyncio.sleep(0.01)

        assert result["started"] is True
        assert manager.is_running() is True

        assert set(feed.calls) == {
            "BTC/USDT",
            "ETH/USDT",
        }

        stopped = await manager.stop()

        assert stopped["stopped"] is True
        assert manager.is_running() is False
        assert exchange.closed is True

    asyncio.run(exercise())


def test_feed_failure_is_counted_and_loop_continues():
    import asyncio

    class FailingFeed:
        def __init__(self):
            self.calls = 0

        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            self.calls += 1

            if self.calls == 1:
                raise RuntimeError(
                    "temporary websocket failure"
                )

            await asyncio.sleep(0)

            return {
                "accepted": True,
                "symbol": symbol,
            }

    feed = FailingFeed()

    manager = CCXTProMultiSymbolFeedManager(
        feed=feed,
        exchange=FakeExchange(),
        symbols=[
            "BTC/USDT",
        ],
        retry_delay_seconds=0.0,
    )

    result = asyncio.run(
        manager.run_cycles(
            cycles_per_symbol=2
        )
    )

    assert result["completed_updates"] == 1
    assert result["failed_updates"] == 1
    assert feed.calls == 2


def test_statistics_are_reported():
    import asyncio

    class RecordingFeed:
        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            await asyncio.sleep(0)

            return {
                "accepted": True,
                "symbol": symbol,
            }

    manager = CCXTProMultiSymbolFeedManager(
        feed=RecordingFeed(),
        exchange=FakeExchange(),
        symbols=[
            "BTC/USDT",
            "ETH/USDT",
        ],
    )

    asyncio.run(
        manager.run_cycles(
            cycles_per_symbol=2
        )
    )

    stats = manager.statistics()

    assert stats["symbols"] == 2
    assert stats["completed_updates"] == 4
    assert stats["failed_updates"] == 0
    assert stats["running"] is False
    assert stats["paper_only"] is True
    assert stats["live_order_submitted"] is False


def test_persistent_loop_updates_statistics():
    import asyncio

    class CountingFeed:
        def __init__(self):
            self.calls = 0

        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            self.calls += 1

            if self.calls == 1:
                raise RuntimeError(
                    "temporary websocket failure"
                )

            await asyncio.sleep(0.001)

            return {
                "accepted": True,
                "symbol": symbol,
            }

    class ClosingExchange:
        async def close(self):
            pass

    feed = CountingFeed()

    manager = CCXTProMultiSymbolFeedManager(
        feed=feed,
        exchange=ClosingExchange(),
        symbols=[
            "BTC/USDT",
        ],
        retry_delay_seconds=0.0,
    )

    async def exercise():
        await manager.start()

        while True:
            stats = manager.statistics()

            if (
                stats["failed_updates"] >= 1
                and stats["completed_updates"] >= 2
            ):
                break

            await asyncio.sleep(0.001)

        await manager.stop()

    asyncio.run(exercise())

    stats = manager.statistics()

    assert stats["failed_updates"] >= 1
    assert stats["completed_updates"] >= 2
    assert stats["running"] is False


def test_persistent_success_records_feed_health():
    import asyncio

    class HealthyFeed:
        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            await asyncio.sleep(0)

            return {
                "accepted": True,
                "symbol": symbol,
            }

    class FakeHealthSupervisor:
        def __init__(self):
            self.successes = []
            self.failures = []

        def record_success(
            self,
            exchange_id,
            symbol,
            latency_ms,
        ):
            self.successes.append({
                "exchange_id": exchange_id,
                "symbol": symbol,
                "latency_ms": latency_ms,
            })

        def record_failure(
            self,
            exchange_id,
            symbol,
            latency_ms,
            reason,
        ):
            self.failures.append({
                "exchange_id": exchange_id,
                "symbol": symbol,
                "latency_ms": latency_ms,
                "reason": reason,
            })

    class Exchange:
        id = "kucoin"

        async def close(self):
            pass

    health = FakeHealthSupervisor()

    manager = CCXTProMultiSymbolFeedManager(
        feed=HealthyFeed(),
        exchange=Exchange(),
        symbols=[
            "BTC/USDT",
        ],
        retry_delay_seconds=0.0,
        health_supervisor=health,
    )

    async def exercise():
        await manager.start()

        while not health.successes:
            await asyncio.sleep(0.001)

        await manager.stop()

    asyncio.run(exercise())

    assert health.successes[0][
        "exchange_id"
    ] == "kucoin"

    assert health.successes[0][
        "symbol"
    ] == "BTC/USDT"

    assert health.failures == []


def test_persistent_failure_records_feed_health():
    import asyncio

    class FailingFeed:
        def __init__(self):
            self.calls = 0

        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            self.calls += 1

            if self.calls == 1:
                raise RuntimeError(
                    "temporary websocket failure"
                )

            await asyncio.sleep(0.001)

            return {
                "accepted": True,
                "symbol": symbol,
            }

    class FakeHealthSupervisor:
        def __init__(self):
            self.successes = []
            self.failures = []

        def record_success(
            self,
            exchange_id,
            symbol,
            latency_ms,
        ):
            self.successes.append({
                "exchange_id": exchange_id,
                "symbol": symbol,
                "latency_ms": latency_ms,
            })

        def record_failure(
            self,
            exchange_id,
            symbol,
            latency_ms,
            reason,
        ):
            self.failures.append({
                "exchange_id": exchange_id,
                "symbol": symbol,
                "latency_ms": latency_ms,
                "reason": reason,
            })

    class Exchange:
        id = "gate"

        async def close(self):
            pass

    health = FakeHealthSupervisor()

    manager = CCXTProMultiSymbolFeedManager(
        feed=FailingFeed(),
        exchange=Exchange(),
        symbols=[
            "ETH/USDT",
        ],
        retry_delay_seconds=0.0,
        health_supervisor=health,
    )

    async def exercise():
        await manager.start()

        while (
            not health.failures
            or not health.successes
        ):
            await asyncio.sleep(0.001)

        await manager.stop()

    asyncio.run(exercise())

    assert health.failures[0][
        "exchange_id"
    ] == "gate"

    assert health.failures[0][
        "symbol"
    ] == "ETH/USDT"

    assert (
        "RuntimeError"
        in health.failures[0][
            "reason"
        ]
    )


def test_persistent_failures_use_backoff_policy():
    import asyncio

    class FailingFeed:
        def __init__(self):
            self.calls = 0

        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            self.calls += 1

            if self.calls <= 2:
                raise RuntimeError(
                    "temporary websocket failure"
                )

            await asyncio.sleep(0.001)

            return {
                "accepted": True,
                "symbol": symbol,
            }

    class FakeBackoffPolicy:
        def __init__(self):
            self.calls = []

        def evaluate(
            self,
            attempt,
            error_type,
            execution_uncertain=False,
        ):
            self.calls.append({
                "attempt": attempt,
                "error_type": error_type,
            })

            return {
                "retry": True,
                "escalate": False,
                "delay_seconds": 0.0,
                "reason": "RETRY_ALLOWED",
            }

    class Exchange:
        id = "kucoin"

        async def close(self):
            pass

    policy = FakeBackoffPolicy()
    feed = FailingFeed()

    manager = CCXTProMultiSymbolFeedManager(
        feed=feed,
        exchange=Exchange(),
        symbols=[
            "BTC/USDT",
        ],
        retry_delay_seconds=0.0,
        backoff_policy=policy,
    )

    async def exercise():
        await manager.start()

        while manager.statistics()[
            "completed_updates"
        ] < 1:
            await asyncio.sleep(0.001)

        await manager.stop()

    asyncio.run(exercise())

    assert [
        item["attempt"]
        for item in policy.calls
    ] == [
        1,
        2,
    ]

    assert all(
        item["error_type"]
        == "NETWORK_ERROR"
        for item in policy.calls
    )


def test_success_resets_backoff_attempt_count():
    import asyncio

    class AlternatingFeed:
        def __init__(self):
            self.calls = 0

        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            self.calls += 1

            if self.calls in {
                1,
                3,
            }:
                raise RuntimeError(
                    "temporary websocket failure"
                )

            await asyncio.sleep(0.001)

            return {
                "accepted": True,
                "symbol": symbol,
            }

    class FakeBackoffPolicy:
        def __init__(self):
            self.attempts = []

        def evaluate(
            self,
            attempt,
            error_type,
            execution_uncertain=False,
        ):
            self.attempts.append(
                attempt
            )

            return {
                "retry": True,
                "escalate": False,
                "delay_seconds": 0.0,
                "reason": "RETRY_ALLOWED",
            }

    class Exchange:
        id = "gate"

        async def close(self):
            pass

    policy = FakeBackoffPolicy()

    manager = CCXTProMultiSymbolFeedManager(
        feed=AlternatingFeed(),
        exchange=Exchange(),
        symbols=[
            "ETH/USDT",
        ],
        retry_delay_seconds=0.0,
        backoff_policy=policy,
    )

    async def exercise():
        await manager.start()

        while (
            manager.statistics()[
                "completed_updates"
            ] < 2
        ):
            await asyncio.sleep(0.001)

        await manager.stop()

    asyncio.run(exercise())

    assert policy.attempts == [
        1,
        1,
    ]


def test_health_snapshot_reports_each_symbol():
    class HealthSupervisor:
        def check_symbol(
            self,
            exchange_id,
            symbol,
        ):
            healthy = (
                symbol != "ETH/USDT"
            )

            return {
                "exchange_id": exchange_id,
                "symbol": symbol,
                "healthy": healthy,
                "reason": (
                    None
                    if healthy
                    else "heartbeat_timeout"
                ),
            }

    class Exchange:
        id = "kucoin"

    manager = CCXTProMultiSymbolFeedManager(
        feed=FakeFeed(),
        exchange=Exchange(),
        symbols=[
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
        ],
        health_supervisor=HealthSupervisor(),
    )

    result = manager.health_snapshot()

    assert result[
        "exchange_id"
    ] == "kucoin"

    assert result[
        "symbol_count"
    ] == 3

    assert result[
        "healthy_symbol_count"
    ] == 2

    assert result[
        "unhealthy_symbol_count"
    ] == 1

    assert result[
        "unhealthy_symbols"
    ] == [
        "ETH/USDT",
    ]

    assert result[
        "symbols"
    ][
        "ETH/USDT"
    ][
        "reason"
    ] == "heartbeat_timeout"


def test_health_snapshot_requires_health_supervisor():
    class Exchange:
        id = "gate"

    manager = CCXTProMultiSymbolFeedManager(
        feed=FakeFeed(),
        exchange=Exchange(),
        symbols=[
            "BTC/USDT",
        ],
    )

    import pytest

    with pytest.raises(
        ValueError,
        match="health_supervisor is required",
    ):
        manager.health_snapshot()


def test_running_manager_applies_symbol_rotation_incrementally():
    import asyncio

    class TrackingFeed:
        def __init__(self):
            self.started = []
            self.cancelled = []

        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            if symbol not in self.started:
                self.started.append(symbol)

            try:
                await asyncio.sleep(3600)
            except asyncio.CancelledError:
                self.cancelled.append(symbol)
                raise

    class Exchange:
        id = "kucoin"

        async def close(self):
            pass

    feed = TrackingFeed()

    manager = CCXTProMultiSymbolFeedManager(
        feed=feed,
        exchange=Exchange(),
        symbols=[
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
        ],
    )

    async def exercise():
        await manager.start()

        while len(feed.started) < 3:
            await asyncio.sleep(0.001)

        result = await manager.apply_symbol_rotation(
            active_symbols=[
                "BTC/USDT",
                "SOL/USDT",
                "XRP/USDT",
            ],
        )

        while "XRP/USDT" not in feed.started:
            await asyncio.sleep(0.001)

        assert result["removed_symbols"] == [
            "ETH/USDT",
        ]

        assert result["added_symbols"] == [
            "XRP/USDT",
        ]

        assert manager.symbols == [
            "BTC/USDT",
            "SOL/USDT",
            "XRP/USDT",
        ]

        assert "ETH/USDT" in feed.cancelled

        assert "BTC/USDT" not in feed.cancelled
        assert "SOL/USDT" not in feed.cancelled

        await manager.stop()

    asyncio.run(exercise())


def test_run_cycles_attributes_failure_to_exchange_symbol_and_exception():
    import asyncio

    class AttributionExchange:
        id = "xt"

    class AttributionFeed:
        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            if symbol == "ETH/USDT":
                raise RuntimeError(
                    "simulated websocket failure"
                )

            return {
                "processed": True,
                "symbol": symbol,
            }

    manager = CCXTProMultiSymbolFeedManager(
        feed=AttributionFeed(),
        exchange=AttributionExchange(),
        symbols=[
            "BTC/USDT",
            "ETH/USDT",
        ],
    )

    result = asyncio.run(
        manager.run_cycles(
            cycles_per_symbol=1,
        )
    )

    assert result["completed_updates"] == 1
    assert result["failed_updates"] == 1

    assert result["failures"] == [
        {
            "exchange_id": "xt",
            "symbol": "ETH/USDT",
            "error_type": "RuntimeError",
            "error": (
                "simulated websocket failure"
            ),
        }
    ]

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_subscription_start_stagger_defaults_to_zero():
    manager = CCXTProMultiSymbolFeedManager(
        feed=FakeFeed(),
        exchange=FakeExchange(),
        symbols=[
            "BTC/USDT",
        ],
    )

    assert (
        manager._subscription_start_stagger_seconds
        == 0.0
    )


def test_subscription_start_stagger_rejects_negative_value():
    import pytest

    with pytest.raises(
        ValueError,
        match=(
            "subscription_start_stagger_seconds "
            "cannot be negative"
        ),
    ):
        CCXTProMultiSymbolFeedManager(
            feed=FakeFeed(),
            exchange=FakeExchange(),
            symbols=[
                "BTC/USDT",
            ],
            subscription_start_stagger_seconds=-0.1,
        )


def test_run_cycles_staggers_symbol_start_times():
    import asyncio
    import time

    class RecordingFeed:
        def __init__(self):
            self.started = {}

        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            self.started[symbol] = (
                time.perf_counter()
            )

            await asyncio.sleep(0)

            return {
                "accepted": True,
                "symbol": symbol,
            }

    feed = RecordingFeed()

    manager = CCXTProMultiSymbolFeedManager(
        feed=feed,
        exchange=FakeExchange(),
        symbols=[
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
        ],
        subscription_start_stagger_seconds=0.03,
    )

    result = asyncio.run(
        manager.run_cycles(
            cycles_per_symbol=1
        )
    )

    assert result["completed_updates"] == 3
    assert result["failed_updates"] == 0

    btc = feed.started["BTC/USDT"]
    eth = feed.started["ETH/USDT"]
    sol = feed.started["SOL/USDT"]

    assert eth - btc >= 0.02
    assert sol - btc >= 0.05


def test_run_cycles_recovers_failed_symbol_when_enabled():
    import asyncio

    class RecoveryExchange:
        id = "kucoin"

    class RecoveryFeed:
        def __init__(self):
            self.calls = {}

        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            self.calls[symbol] = (
                self.calls.get(symbol, 0) + 1
            )

            if (
                symbol == "ACS/USDT"
                and self.calls[symbol] == 1
            ):
                raise TimeoutError()

            await asyncio.sleep(0)

            return {
                "accepted": True,
                "symbol": symbol,
            }

    feed = RecoveryFeed()

    manager = CCXTProMultiSymbolFeedManager(
        feed=feed,
        exchange=RecoveryExchange(),
        symbols=[
            "BTC/USDT",
            "ACS/USDT",
        ],
        recovery_attempts=1,
        recovery_delay_seconds=0.0,
    )

    result = asyncio.run(
        manager.run_cycles(
            cycles_per_symbol=1,
        )
    )

    assert feed.calls["BTC/USDT"] == 1
    assert feed.calls["ACS/USDT"] == 2

    assert result["completed_updates"] == 2
    assert result["failed_updates"] == 0

    assert result["initial_failed_updates"] == 1
    assert result["recovery_attempts"] == 1
    assert result["recovered_updates"] == 1
    assert result["unrecovered_failures"] == 0
    assert result["failures"] == []

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_run_cycles_reports_persistent_failure_after_recovery():
    import asyncio

    class RecoveryExchange:
        id = "kucoin"

    class FailingFeed:
        def __init__(self):
            self.calls = {}

        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            self.calls[symbol] = (
                self.calls.get(symbol, 0) + 1
            )

            if symbol == "ACS/USDT":
                raise TimeoutError()

            await asyncio.sleep(0)

            return {
                "accepted": True,
                "symbol": symbol,
            }

    feed = FailingFeed()

    manager = CCXTProMultiSymbolFeedManager(
        feed=feed,
        exchange=RecoveryExchange(),
        symbols=[
            "BTC/USDT",
            "ACS/USDT",
        ],
        recovery_attempts=1,
        recovery_delay_seconds=0.0,
    )

    result = asyncio.run(
        manager.run_cycles(
            cycles_per_symbol=1,
        )
    )

    assert feed.calls["BTC/USDT"] == 1
    assert feed.calls["ACS/USDT"] == 2

    assert result["completed_updates"] == 1
    assert result["failed_updates"] == 1

    assert result["initial_failed_updates"] == 1
    assert result["recovery_attempts"] == 1
    assert result["recovered_updates"] == 0
    assert result["unrecovered_failures"] == 1

    assert result["failures"] == [
        {
            "exchange_id": "kucoin",
            "symbol": "ACS/USDT",
            "error_type": "TimeoutError",
            "error": "",
        }
    ]


def test_recovery_defaults_to_disabled():
    manager = CCXTProMultiSymbolFeedManager(
        feed=FakeFeed(),
        exchange=FakeExchange(),
        symbols=[
            "BTC/USDT",
        ],
    )

    assert manager._recovery_attempts == 0
    assert manager._recovery_delay_seconds == 1.0


def test_recovery_configuration_rejects_negative_values():
    import pytest

    with pytest.raises(
        ValueError,
        match="recovery_attempts cannot be negative",
    ):
        CCXTProMultiSymbolFeedManager(
            feed=FakeFeed(),
            exchange=FakeExchange(),
            symbols=[
                "BTC/USDT",
            ],
            recovery_attempts=-1,
        )

    with pytest.raises(
        ValueError,
        match=(
            "recovery_delay_seconds "
            "cannot be negative"
        ),
    ):
        CCXTProMultiSymbolFeedManager(
            feed=FakeFeed(),
            exchange=FakeExchange(),
            symbols=[
                "BTC/USDT",
            ],
            recovery_delay_seconds=-0.1,
        )


def test_persistent_start_staggers_symbol_subscriptions():
    import asyncio
    import time

    class RecordingFeed:
        def __init__(self):
            self.started = {}

        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            if symbol not in self.started:
                self.started[
                    symbol
                ] = time.perf_counter()

            await asyncio.sleep(3600)

    class Exchange:
        id = "kucoin"

        async def close(self):
            pass

    feed = RecordingFeed()

    manager = CCXTProMultiSymbolFeedManager(
        feed=feed,
        exchange=Exchange(),
        symbols=[
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
        ],
        subscription_start_stagger_seconds=0.03,
    )

    async def exercise():
        await manager.start()

        while len(feed.started) < 3:
            await asyncio.sleep(0.001)

        await manager.stop()

    asyncio.run(exercise())

    btc = feed.started["BTC/USDT"]
    eth = feed.started["ETH/USDT"]
    sol = feed.started["SOL/USDT"]

    assert eth - btc >= 0.02
    assert sol - btc >= 0.05


def test_stop_during_persistent_start_stagger_prevents_late_start():
    import asyncio

    class RecordingFeed:
        def __init__(self):
            self.started = []

        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            self.started.append(symbol)
            await asyncio.sleep(3600)

    class Exchange:
        id = "kucoin"

        async def close(self):
            pass

    feed = RecordingFeed()

    manager = CCXTProMultiSymbolFeedManager(
        feed=feed,
        exchange=Exchange(),
        symbols=[
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
        ],
        subscription_start_stagger_seconds=0.1,
    )

    async def exercise():
        await manager.start()

        while "BTC/USDT" not in feed.started:
            await asyncio.sleep(0.001)

        await manager.stop()

        await asyncio.sleep(0.12)

    asyncio.run(exercise())

    assert feed.started == [
        "BTC/USDT",
    ]


def test_running_symbol_rotation_does_not_use_full_start_stagger():
    import asyncio

    class RecordingFeed:
        def __init__(self):
            self.started = []

        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            if symbol not in self.started:
                self.started.append(symbol)

            await asyncio.sleep(3600)

    class Exchange:
        id = "kucoin"

        async def close(self):
            pass

    feed = RecordingFeed()

    manager = CCXTProMultiSymbolFeedManager(
        feed=feed,
        exchange=Exchange(),
        symbols=[
            "BTC/USDT",
        ],
        subscription_start_stagger_seconds=1.0,
    )

    async def exercise():
        await manager.start()

        while "BTC/USDT" not in feed.started:
            await asyncio.sleep(0.001)

        await manager.apply_symbol_rotation(
            active_symbols=[
                "BTC/USDT",
                "XRP/USDT",
            ]
        )

        for _ in range(100):
            if "XRP/USDT" in feed.started:
                break

            await asyncio.sleep(0.001)

        assert "XRP/USDT" in feed.started

        await manager.stop()

    asyncio.run(exercise())


def test_stop_is_idempotent_after_persistent_run():
    import asyncio

    class Feed:
        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            await asyncio.sleep(3600)

    class Exchange:
        id = "binance"

        def __init__(self):
            self.close_calls = 0

        async def close(self):
            self.close_calls += 1

    exchange = Exchange()

    manager = CCXTProMultiSymbolFeedManager(
        feed=Feed(),
        exchange=exchange,
        symbols=[
            "BTC/USDT",
            "ETH/USDT",
        ],
    )

    async def exercise():
        await manager.start()

        await asyncio.sleep(0)

        first = await manager.stop()
        second = await manager.stop()

        return first, second

    first, second = asyncio.run(
        exercise()
    )

    assert first["stopped"] is True
    assert first["task_count"] == 2
    assert first["cancelled_task_count"] == 2
    assert first["task_error_count"] == 0
    assert first["close_error"] is None

    assert second["stopped"] is True
    assert second["already_stopped"] is True
    assert second["task_count"] == 0

    assert manager.is_running() is False


def test_stop_waits_for_cancelled_persistent_tasks_before_exchange_close():
    import asyncio

    events = []

    class Feed:
        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            events.append(
                f"watch:{symbol}"
            )

            try:
                await asyncio.sleep(3600)

            except asyncio.CancelledError:
                events.append(
                    f"cancel:{symbol}"
                )
                raise

    class Exchange:
        id = "xt"

        async def close(self):
            events.append(
                "exchange_close"
            )

    manager = CCXTProMultiSymbolFeedManager(
        feed=Feed(),
        exchange=Exchange(),
        symbols=[
            "BTC/USDT",
            "ETH/USDT",
        ],
    )

    async def exercise():
        await manager.start()

        while (
            len(
                [
                    event
                    for event in events
                    if event.startswith(
                        "watch:"
                    )
                ]
            )
            < 2
        ):
            await asyncio.sleep(0)

        await manager.stop()

    asyncio.run(
        exercise()
    )

    close_index = events.index(
        "exchange_close"
    )

    cancel_indexes = [
        index
        for index, event
        in enumerate(events)
        if event.startswith(
            "cancel:"
        )
    ]

    assert len(cancel_indexes) == 2

    assert all(
        index < close_index
        for index in cancel_indexes
    )


def test_persistent_statistics_reports_recent_failure_details():
    import asyncio

    class FailingFeed:
        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            raise RuntimeError(
                f"diagnostic websocket failure: {symbol}"
            )

    class Exchange:
        id = "kucoin"

        async def close(self):
            pass

    manager = CCXTProMultiSymbolFeedManager(
        feed=FailingFeed(),
        exchange=Exchange(),
        symbols=[
            "BTC/USDT",
        ],
        retry_delay_seconds=0.01,
    )

    async def exercise():
        await manager.start()

        for _ in range(1000):
            if (
                manager.statistics()[
                    "failed_updates"
                ]
                >= 1
            ):
                break

            await asyncio.sleep(0.001)

        result = manager.statistics()

        await manager.stop()

        return result

    result = asyncio.run(
        exercise()
    )

    assert result["failed_updates"] >= 1

    assert result["recent_failures"]

    failure = result["recent_failures"][-1]

    assert failure == {
        "exchange_id": "kucoin",
        "symbol": "BTC/USDT",
        "error_type": "RuntimeError",
        "error": (
            "diagnostic websocket failure: BTC/USDT"
        ),
    }

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_persistent_recent_failures_are_bounded_and_diagnostic():
    import asyncio

    class FailingFeed:
        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            raise RuntimeError(
                f"bounded diagnostic failure: {symbol}"
            )

    class Exchange:
        id = "binance"

        async def close(self):
            pass

    manager = CCXTProMultiSymbolFeedManager(
        feed=FailingFeed(),
        exchange=Exchange(),
        symbols=[
            "BTC/USDT",
        ],
        retry_delay_seconds=0.001,
    )

    async def exercise():
        await manager.start()

        for _ in range(2000):
            result = manager.statistics()

            if result["failed_updates"] >= 20:
                break

            await asyncio.sleep(0.001)

        result = manager.statistics()

        await manager.stop()

        return result

    result = asyncio.run(
        exercise()
    )

    assert result["failed_updates"] >= 20

    failures = result["recent_failures"]

    assert failures
    assert len(failures) <= 20

    latest = failures[-1]

    assert latest["exchange_id"] == "binance"
    assert latest["symbol"] == "BTC/USDT"
    assert latest["error_type"] == "RuntimeError"

    assert (
        "bounded diagnostic failure: BTC/USDT"
        in latest["error"]
    )






def test_persistent_start_respects_max_concurrent_symbol_starts():
    import asyncio

    class ConcurrencyFeed:
        def __init__(self):
            self.first_started = set()

            self.active_first = 0
            self.max_active_first = 0

            self.release_first = (
                asyncio.Event()
            )

            self.hold_steady_state = (
                asyncio.Event()
            )

            self.calls = {}

        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            call_number = (
                self.calls.get(symbol, 0)
                + 1
            )

            self.calls[symbol] = call_number

            if call_number == 1:
                self.first_started.add(
                    symbol
                )

                self.active_first += 1

                self.max_active_first = max(
                    self.max_active_first,
                    self.active_first,
                )

                try:
                    await self.release_first.wait()

                finally:
                    self.active_first -= 1

                return {
                    "accepted": True,
                    "symbol": symbol,
                }

            # Once a symbol has completed its initial
            # subscription/update, its steady-state
            # watch must NOT retain a startup permit.
            await self.hold_steady_state.wait()

            return {
                "accepted": True,
                "symbol": symbol,
            }

    class Exchange:
        id = "gate"

        async def close(self):
            pass

    async def exercise():
        symbols = [
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
            "XRP/USDT",
            "ADA/USDT",
            "DOGE/USDT",
        ]

        feed = ConcurrencyFeed()

        manager = CCXTProMultiSymbolFeedManager(
            feed=feed,
            exchange=Exchange(),
            symbols=symbols,
            retry_delay_seconds=0.0,
            max_concurrent_symbol_starts=2,
        )

        await manager.start()

        for _ in range(200):
            if len(feed.first_started) >= 2:
                break

            await asyncio.sleep(0.001)

        assert len(feed.first_started) == 2

        assert (
            feed.max_active_first
            == 2
        )

        # Allow initialized symbols to move into
        # steady-state watches. Their startup slots
        # must then become available to the remaining
        # symbols.
        feed.release_first.set()

        for _ in range(500):
            if (
                len(feed.first_started)
                == len(symbols)
            ):
                break

            await asyncio.sleep(0.001)

        assert (
            len(feed.first_started)
            == len(symbols)
        )

        assert (
            feed.max_active_first
            <= 2
        )

        await manager.stop()

    asyncio.run(exercise())

def test_symbol_rotation_respects_max_concurrent_symbol_starts():
    import asyncio

    class RotationConcurrencyFeed:
        def __init__(self):
            self.calls = {}

            self.initial_symbols = {
                "BTC/USDT",
                "ETH/USDT",
            }

            self.rotation_symbols = {
                "SOL/USDT",
                "XRP/USDT",
                "ADA/USDT",
                "DOGE/USDT",
            }

            self.initial_started = set()

            self.rotation_first_started = set()

            self.active_rotation_first = 0
            self.max_active_rotation_first = 0

            self.release_initial = asyncio.Event()
            self.release_rotation = asyncio.Event()
            self.hold_steady_state = asyncio.Event()

        async def watch_once(
            self,
            symbol,
            limit=None,
        ):
            call_number = (
                self.calls.get(symbol, 0)
                + 1
            )

            self.calls[symbol] = call_number

            if (
                symbol in self.initial_symbols
                and call_number == 1
            ):
                self.initial_started.add(
                    symbol
                )

                await self.release_initial.wait()

                return {
                    "accepted": True,
                    "symbol": symbol,
                }

            if (
                symbol in self.rotation_symbols
                and call_number == 1
            ):
                self.rotation_first_started.add(
                    symbol
                )

                self.active_rotation_first += 1

                self.max_active_rotation_first = max(
                    self.max_active_rotation_first,
                    self.active_rotation_first,
                )

                try:
                    await self.release_rotation.wait()
                finally:
                    self.active_rotation_first -= 1

                return {
                    "accepted": True,
                    "symbol": symbol,
                }

            # A successfully initialized symbol may remain
            # indefinitely in steady state without retaining
            # a startup permit.
            await self.hold_steady_state.wait()

            return {
                "accepted": True,
                "symbol": symbol,
            }

    class Exchange:
        id = "gate"

        async def close(self):
            pass

    async def exercise():
        feed = RotationConcurrencyFeed()

        manager = CCXTProMultiSymbolFeedManager(
            feed=feed,
            exchange=Exchange(),
            symbols=[
                "BTC/USDT",
                "ETH/USDT",
            ],
            retry_delay_seconds=0.0,
            max_concurrent_symbol_starts=2,
        )

        await manager.start()

        # Both original symbols should occupy the two
        # startup permits.
        for _ in range(200):
            if len(feed.initial_started) == 2:
                break

            await asyncio.sleep(0.001)

        assert len(feed.initial_started) == 2

        # Complete their first successful update. They
        # should then release their startup permits and
        # enter unrestricted steady state.
        feed.release_initial.set()

        for _ in range(200):
            if (
                feed.calls.get("BTC/USDT", 0) >= 2
                and
                feed.calls.get("ETH/USDT", 0) >= 2
            ):
                break

            await asyncio.sleep(0.001)

        assert (
            feed.calls.get("BTC/USDT", 0)
            >= 2
        )

        assert (
            feed.calls.get("ETH/USDT", 0)
            >= 2
        )

        # Now introduce four new symbols while the
        # original symbols remain blocked in steady state.
        await manager.apply_symbol_rotation(
            active_symbols=[
                "BTC/USDT",
                "ETH/USDT",
                "SOL/USDT",
                "XRP/USDT",
                "ADA/USDT",
                "DOGE/USDT",
            ]
        )

        for _ in range(200):
            if (
                len(feed.rotation_first_started)
                >= 2
            ):
                break

            await asyncio.sleep(0.001)

        # Exactly two rotated symbols should be allowed
        # through the startup gate initially.
        assert (
            len(feed.rotation_first_started)
            == 2
        )

        assert (
            feed.max_active_rotation_first
            == 2
        )

        # Release the first pair. The remaining rotated
        # symbols should then acquire the freed permits.
        feed.release_rotation.set()

        for _ in range(500):
            if (
                len(feed.rotation_first_started)
                == 4
            ):
                break

            await asyncio.sleep(0.001)

        assert (
            len(feed.rotation_first_started)
            == 4
        )

        assert (
            feed.max_active_rotation_first
            <= 2
        )

        await manager.stop()

    asyncio.run(exercise())
