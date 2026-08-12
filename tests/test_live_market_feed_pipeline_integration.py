import asyncio

from core.ccxt_pro_multi_symbol_feed_manager import (
    CCXTProMultiSymbolFeedManager,
)
from core.live_market_data_intake_service import (
    LiveMarketDataIntakeService,
)
from core.live_market_event_dispatcher import (
    LiveMarketEventDispatcher,
)
from core.live_market_route_work_queue import (
    LiveMarketRouteWorkQueue,
)
from core.route_dependency_registry import (
    RouteDependencyRegistry,
)
from core.shared_live_market_data_cache import (
    SharedLiveMarketDataCache,
)


class IntakeFeed:
    def __init__(
        self,
        intake,
    ):
        self._intake = intake
        self.sequence = 0

    async def watch_once(
        self,
        symbol,
        limit=None,
    ):
        self.sequence += 1

        result = self._intake.submit({
            "exchange_id": "kucoin",
            "symbol": symbol,
            "sequence": self.sequence,
            "timestamp": float(
                self.sequence
            ),
            "bid": 100.0,
            "ask": 101.0,
            "priority": 5.0,
        })

        await asyncio.sleep(0)

        return result


class FakeExchange:
    async def close(self):
        pass


def test_feed_update_queues_only_dependent_route():
    registry = RouteDependencyRegistry()

    registry.register({
        "route_id": "R-BTC",
        "exchange_id": "kucoin",
        "legs": [
            {
                "symbol": "BTC/USDT",
                "side": "buy",
            },
        ],
    })

    registry.register({
        "route_id": "R-ETH",
        "exchange_id": "kucoin",
        "legs": [
            {
                "symbol": "ETH/USDT",
                "side": "buy",
            },
        ],
    })

    queue = LiveMarketRouteWorkQueue(
        max_queue_size=100
    )

    dispatcher = LiveMarketEventDispatcher(
        work_queue=queue,
        route_registry=registry,
    )

    intake = LiveMarketDataIntakeService(
        cache=SharedLiveMarketDataCache(),
        dispatcher=dispatcher,
    )

    manager = CCXTProMultiSymbolFeedManager(
        feed=IntakeFeed(intake),
        exchange=FakeExchange(),
        symbols=[
            "BTC/USDT",
        ],
    )

    result = asyncio.run(
        manager.run_cycles(
            cycles_per_symbol=1
        )
    )

    assert result[
        "completed_updates"
    ] == 1

    assert queue.pending_count() == 1

    work = queue.dequeue()

    assert work["route_id"] == "R-BTC"
    assert work["symbol"] == "BTC/USDT"
    assert work["sequence"] == 1

    assert queue.pending_count() == 0

    assert result["paper_only"] is True
    assert (
        result["live_order_submitted"]
        is False
    )
