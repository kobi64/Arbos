"""
ArbOS™

EX-354
Event-Driven Shared-Cache Scan Engine

Connects the existing ArbOS market cache, dependency
registry, dispatcher, work queue and worker pool into one
paper-safe route evaluation engine.

Architecture:

market snapshot
    -> SharedLiveMarketDataCache
    -> LiveMarketEventDispatcher
    -> LiveMarketRouteWorkQueue
    -> ContinuousRouteWorkerPool
    -> route evaluation from shared cache

No authentication.
No transfers.
No live orders.
"""

from core.shared_live_market_data_cache import (
    SharedLiveMarketDataCache,
)
from core.route_dependency_registry import (
    RouteDependencyRegistry,
)
from core.live_market_route_work_queue import (
    LiveMarketRouteWorkQueue,
)
from core.live_market_event_dispatcher import (
    LiveMarketEventDispatcher,
)
from core.continuous_route_worker_pool import (
    ContinuousRouteWorkerPool,
)


class EventDrivenSharedCacheScanEngine:
    def __init__(
        self,
        worker_factory,
        worker_count=8,
        max_queue_size=100000,
        market_cache=None,
        route_registry=None,
        work_queue=None,
    ):
        if worker_factory is None:
            raise ValueError(
                "worker_factory is required"
            )

        if worker_count <= 0:
            raise ValueError(
                "worker_count must be positive"
            )

        self._worker_factory = (
            worker_factory
        )

        self._worker_count = int(
            worker_count
        )

        self._market_cache = (
            market_cache
            or SharedLiveMarketDataCache()
        )

        self._route_registry = (
            route_registry
            or RouteDependencyRegistry()
        )

        self._work_queue = (
            work_queue
            or LiveMarketRouteWorkQueue(
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

    @property
    def market_cache(self):
        return self._market_cache

    @property
    def route_registry(self):
        return self._route_registry

    @property
    def work_queue(self):
        return self._work_queue

    @property
    def dispatcher(self):
        return self._dispatcher

    def register_route(
        self,
        route,
    ):
        return self._route_registry.register(
            route
        )

    def publish(
        self,
        snapshot,
    ):
        if snapshot is None:
            raise ValueError(
                "snapshot is required"
            )

        result = self._market_cache.update(
            snapshot
        )

        if result.get(
            "updated"
        ) is not True:
            return {
                **result,
                "dispatched": False,
                "paper_only": True,
                "live_order_submitted": False,
            }

        dispatch = self._dispatcher.dispatch({
            "exchange_id": snapshot[
                "exchange_id"
            ],
            "symbol": snapshot[
                "symbol"
            ],
            "sequence": snapshot.get(
                "sequence"
            ),
            "priority": snapshot.get(
                "priority",
                0.0,
            ),
        })

        return {
            **result,
            "dispatched": True,
            "dispatch": dispatch,
            "paper_only": True,
            "live_order_submitted": False,
        }

    def publish_many(
        self,
        snapshots,
    ):
        published = 0
        dispatched = 0
        rejected = 0
        queued_route_ids = set()

        results = []

        for snapshot in snapshots or []:
            result = self.publish(
                snapshot
            )

            results.append(
                result
            )

            if result.get(
                "updated"
            ) is True:
                published += 1
            else:
                rejected += 1

            if result.get(
                "dispatched"
            ) is True:
                dispatched += 1

                dispatch = result.get(
                    "dispatch"
                ) or {}

                queued_route_ids.update(
                    dispatch.get(
                        "queued_route_ids",
                        [],
                    )
                )

        return {
            "published_snapshot_count": (
                published
            ),
            "dispatched_snapshot_count": (
                dispatched
            ),
            "rejected_snapshot_count": (
                rejected
            ),
            "queued_route_count": len(
                queued_route_ids
            ),
            "queued_route_ids": sorted(
                queued_route_ids
            ),
            "pending_count": (
                self._work_queue.pending_count()
            ),
            "results": results,
            "paper_only": True,
            "live_order_submitted": False,
        }

    def process_pending(
        self,
        max_items=None,
    ):
        pool = ContinuousRouteWorkerPool(
            worker_count=self._worker_count,
            work_queue=self._work_queue,
            market_cache=self._market_cache,
            route_registry=(
                self._route_registry
            ),
            worker_factory=(
                self._worker_factory
            ),
        )

        result = pool.run_until_empty(
            max_items=max_items
        )

        return {
            **result,
            "paper_only": True,
            "live_order_submitted": (
                bool(
                    result.get(
                        "live_order_submitted",
                        False,
                    )
                )
            ),
        }

    def run_batch(
        self,
        snapshots,
    ):
        publication = self.publish_many(
            snapshots
        )

        processing = self.process_pending()

        live_order_submitted = bool(
            publication.get(
                "live_order_submitted",
                False,
            )
            or processing.get(
                "live_order_submitted",
                False,
            )
        )

        return {
            "publication": publication,
            "processing": processing,
            "registered_route_count": (
                self._route_registry.route_count()
            ),
            "worker_count": (
                self._worker_count
            ),
            "paper_only": True,
            "live_order_submitted": (
                live_order_submitted
            ),
        }
