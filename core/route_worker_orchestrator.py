"""
ArbOS™
EX-204
Route Worker Orchestrator

Coordinates the central route registry, live market dispatcher,
coalescing route work queue, and shared-cache route worker.

Route definitions are registered once through the central registry.
Both dispatcher and worker consume that same source of truth.

Paper-safe infrastructure only.
No authentication.
No transfers.
No live orders.
"""

from core.live_market_event_dispatcher import (
    LiveMarketEventDispatcher,
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


class RouteWorkerOrchestrator:
    def __init__(
        self,
        market_cache,
        max_queue_size,
        worker_factory=SharedCacheRouteWorker,
        route_registry=None,
        work_queue=None,
    ):
        if market_cache is None:
            raise ValueError(
                "market_cache is required"
            )

        if worker_factory is None:
            raise ValueError(
                "worker_factory is required"
            )

        self._market_cache = (
            market_cache
        )

        self._route_registry = (
            route_registry
            if route_registry is not None
            else RouteDependencyRegistry()
        )

        self._work_queue = (
            work_queue
            if work_queue is not None
            else LiveMarketRouteWorkQueue(
                max_queue_size=max_queue_size
            )
        )

        self._dispatcher = (
            LiveMarketEventDispatcher(
                work_queue=self._work_queue,
                route_registry=(
                    self._route_registry
                ),
            )
        )

        self._worker = worker_factory(
            work_queue=self._work_queue,
            market_cache=self._market_cache,
            route_registry=(
                self._route_registry
            ),
        )

    @property
    def route_registry(
        self,
    ):
        return self._route_registry

    @property
    def work_queue(
        self,
    ):
        return self._work_queue

    @property
    def dispatcher(
        self,
    ):
        return self._dispatcher

    @property
    def worker(
        self,
    ):
        return self._worker

    def register_route(
        self,
        route,
    ):
        return self._route_registry.register(
            route
        )

    def dispatch(
        self,
        event,
    ):
        return self._dispatcher.dispatch(
            event
        )

    def process_next(
        self,
    ):
        return self._worker.process_next()

    def process_until_empty(
        self,
    ):
        processed = []

        while (
            self._work_queue.pending_count()
            > 0
        ):
            result = (
                self._worker.process_next()
            )

            if result is None:
                break

            processed.append(
                result
            )

        return {
            "processed_count": len(
                processed
            ),
            "results": processed,
            "remaining_count": (
                self._work_queue
                .pending_count()
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def pending_count(
        self,
    ):
        return (
            self._work_queue
            .pending_count()
        )
