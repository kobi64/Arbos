import asyncio

from core.ccxt_pro_multi_symbol_feed_manager import (
    CCXTProMultiSymbolFeedManager,
)
from core.dynamic_feed_capacity_application_planner import (
    DynamicFeedCapacityApplicationPlanner,
)
from core.dynamic_feed_capacity_controller import (
    DynamicFeedCapacityController,
)
from core.dynamic_feed_capacity_orchestrator import (
    DynamicFeedCapacityOrchestrator,
)


class BlockingFeed:
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


class HealthSupervisor:
    def check_symbol(
        self,
        exchange_id,
        symbol,
    ):
        unhealthy = (
            symbol == "COIN4/USDT"
        )

        return {
            "exchange_id": exchange_id,
            "symbol": symbol,
            "healthy": not unhealthy,
            "reason": (
                "heartbeat_timeout"
                if unhealthy
                else None
            ),
        }

    def record_success(
        self,
        exchange_id,
        symbol,
        latency_ms,
    ):
        pass

    def record_failure(
        self,
        exchange_id,
        symbol,
        latency_ms,
        reason,
    ):
        pass


class Exchange:
    id = "kucoin"

    async def close(self):
        pass


def profile():
    return {
        "exchange_id": "kucoin",
        "max_symbols_per_batch": 1,
        "max_batches": 4,
        "max_total_symbols": 4,
    }


def test_unhealthy_feed_causes_incremental_capacity_reduction():
    feed = BlockingFeed()

    manager = CCXTProMultiSymbolFeedManager(
        feed=feed,
        exchange=Exchange(),
        symbols=[
            "COIN1/USDT",
            "COIN2/USDT",
            "COIN3/USDT",
            "COIN4/USDT",
        ],
        health_supervisor=HealthSupervisor(),
    )

    controller = DynamicFeedCapacityController(
        profile=profile(),
        unhealthy_confirmations=1,
        healthy_confirmations=1,
    )

    orchestrator = DynamicFeedCapacityOrchestrator(
        manager=manager,
        capacity_controller=controller,
        application_planner=(
            DynamicFeedCapacityApplicationPlanner()
        ),
        active_symbols=[
            "COIN1/USDT",
            "COIN2/USDT",
            "COIN3/USDT",
            "COIN4/USDT",
        ],
        overflow_symbols=[
            "WAIT1/USDT",
        ],
    )

    async def exercise():
        await manager.start()

        while len(feed.started) < 4:
            await asyncio.sleep(0.001)

        result = await orchestrator.rebalance()

        assert result["action"] == "scale_down"

        assert result["active_symbols"] == [
            "COIN1/USDT",
            "COIN2/USDT",
            "COIN3/USDT",
        ]

        assert result["overflow_symbols"] == [
            "COIN4/USDT",
            "WAIT1/USDT",
        ]

        assert manager.symbols == [
            "COIN1/USDT",
            "COIN2/USDT",
            "COIN3/USDT",
        ]

        assert "COIN4/USDT" in feed.cancelled

        assert "COIN1/USDT" not in feed.cancelled
        assert "COIN2/USDT" not in feed.cancelled
        assert "COIN3/USDT" not in feed.cancelled

        await manager.stop()

    asyncio.run(exercise())
