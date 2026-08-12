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
