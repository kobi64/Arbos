"""
ArbOS™

EX-356
Queued Cross-Exchange Shared Cache Route Worker

Queue-compatible adapter around EX-353.

Consumes one coalesced route work item and evaluates the
cross-exchange route entirely from SharedLiveMarketDataCache.

No exchange API calls during route evaluation.
Paper only.
No authentication.
No transfers.
No live orders.
"""

from core.cross_exchange_shared_cache_route_worker import (
    CrossExchangeSharedCacheRouteWorker,
)


class QueuedCrossExchangeSharedCacheRouteWorker:
    def __init__(
        self,
        work_queue,
        market_cache,
        route_registry,
    ):
        if work_queue is None:
            raise ValueError(
                "work_queue is required"
            )

        if market_cache is None:
            raise ValueError(
                "market_cache is required"
            )

        if route_registry is None:
            raise ValueError(
                "route_registry is required"
            )

        self._work_queue = work_queue

        self._evaluator = (
            CrossExchangeSharedCacheRouteWorker(
                market_cache=market_cache,
                route_registry=route_registry,
            )
        )

    def process_next(self):
        work = self._work_queue.dequeue()

        if work is None:
            return None

        result = self._evaluator.evaluate(
            work.get("route_id")
        )

        return {
            **result,
            "work_sequence": (
                work.get("sequence")
            ),
            "trigger_exchange_id": (
                work.get("exchange_id")
            ),
            "trigger_symbol": (
                work.get("symbol")
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
