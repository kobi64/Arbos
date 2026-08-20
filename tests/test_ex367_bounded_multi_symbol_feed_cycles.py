"""
ArbOS™

EX-367
Bounded Multi-Symbol Feed Cycles

Verifies that a silent WebSocket subscription cannot block
the complete multi-symbol feed cycle.

Public market data only.
No authentication.
No transfers.
No live orders.
"""

import asyncio

import pytest

from core.ccxt_pro_multi_symbol_feed_manager import (
    CCXTProMultiSymbolFeedManager,
)


class FakeExchange:
    id = "fake"


class ControlledFeed:
    def __init__(
        self,
        silent_symbols=None,
        failed_symbols=None,
    ):
        self.silent_symbols = set(
            silent_symbols or []
        )
        self.failed_symbols = set(
            failed_symbols or []
        )
        self.calls = []

    async def watch_once(
        self,
        symbol,
        limit=None,
    ):
        self.calls.append(symbol)

        if symbol in self.silent_symbols:
            await asyncio.Event().wait()

        if symbol in self.failed_symbols:
            raise RuntimeError(
                "simulated feed failure"
            )

        await asyncio.sleep(0)

        return {
            "symbol": symbol,
            "paper_only": True,
            "live_order_submitted": False,
        }


def build_manager(
    feed,
    symbols,
    timeout=0.05,
):
    return CCXTProMultiSymbolFeedManager(
        feed=feed,
        exchange=FakeExchange(),
        symbols=symbols,
        retry_delay_seconds=0.0,
        cycle_timeout_seconds=timeout,
    )


def test_rejects_non_positive_cycle_timeout():
    with pytest.raises(
        ValueError,
        match=(
            "cycle_timeout_seconds "
            "must be positive"
        ),
    ):
        build_manager(
            ControlledFeed(),
            ["BTC/USDT"],
            timeout=0,
        )


def test_healthy_symbol_completes():
    async def scenario():
        manager = build_manager(
            ControlledFeed(),
            ["BTC/USDT"],
        )

        result = await manager.run_cycles()

        assert result[
            "completed_updates"
        ] == 1
        assert result[
            "failed_updates"
        ] == 0

    asyncio.run(scenario())


def test_silent_symbol_times_out():
    async def scenario():
        manager = build_manager(
            ControlledFeed(
                silent_symbols={
                    "ETH/USDT"
                }
            ),
            ["ETH/USDT"],
        )

        result = await asyncio.wait_for(
            manager.run_cycles(),
            timeout=0.5,
        )

        assert result[
            "completed_updates"
        ] == 0
        assert result[
            "failed_updates"
        ] == 1

    asyncio.run(scenario())


def test_silent_symbol_does_not_block_healthy_symbols():
    async def scenario():
        feed = ControlledFeed(
            silent_symbols={
                "ETH/USDT"
            }
        )

        manager = build_manager(
            feed,
            [
                "BTC/USDT",
                "ETH/USDT",
                "SOL/USDT",
            ],
        )

        result = await asyncio.wait_for(
            manager.run_cycles(),
            timeout=0.5,
        )

        assert result[
            "completed_updates"
        ] == 2
        assert result[
            "failed_updates"
        ] == 1

        assert set(feed.calls) == {
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
        }

    asyncio.run(scenario())


def test_failure_and_timeout_are_both_bounded():
    async def scenario():
        feed = ControlledFeed(
            silent_symbols={
                "ETH/USDT"
            },
            failed_symbols={
                "DOGE/USDT"
            },
        )

        manager = build_manager(
            feed,
            [
                "BTC/USDT",
                "ETH/USDT",
                "SOL/USDT",
                "DOGE/USDT",
            ],
        )

        result = await asyncio.wait_for(
            manager.run_cycles(),
            timeout=0.5,
        )

        assert result[
            "completed_updates"
        ] == 2
        assert result[
            "failed_updates"
        ] == 2
        assert result[
            "symbol_count"
        ] == 4
        assert result[
            "paper_only"
        ] is True
        assert result[
            "live_order_submitted"
        ] is False

    asyncio.run(scenario())
