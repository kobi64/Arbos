"""
ArbOS™
EX-205
Continuous Route Worker Pool

Runs multiple route workers concurrently against the same
thread-safe route work queue, shared market cache, and
central route registry.

This is a bounded worker pool for continuous paper-route
recalculation.

Paper-safe infrastructure only.
No authentication.
No transfers.
No live orders.
"""

import threading


class ContinuousRouteWorkerPool:
    def __init__(
        self,
        worker_count,
        work_queue,
        market_cache,
        route_registry,
        worker_factory,
    ):
        if worker_count <= 0:
            raise ValueError(
                "worker_count must be positive"
            )

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

        if worker_factory is None:
            raise ValueError(
                "worker_factory is required"
            )

        self._worker_count = int(
            worker_count
        )

        self._work_queue = (
            work_queue
        )

        self._market_cache = (
            market_cache
        )

        self._route_registry = (
            route_registry
        )

        self._worker_factory = (
            worker_factory
        )

    def run_until_empty(
        self,
    ):
        results = []
        results_lock = (
            threading.Lock()
        )

        workers = [
            self._worker_factory(
                work_queue=(
                    self._work_queue
                ),
                market_cache=(
                    self._market_cache
                ),
                route_registry=(
                    self._route_registry
                ),
            )
            for _ in range(
                self._worker_count
            )
        ]

        def run_worker(
            worker,
        ):
            while True:
                result = (
                    worker.process_next()
                )

                if result is None:
                    break

                with results_lock:
                    results.append(
                        result
                    )

        threads = [
            threading.Thread(
                target=run_worker,
                args=(worker,),
            )
            for worker in workers
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        return {
            "worker_count": (
                self._worker_count
            ),
            "processed_count": len(
                results
            ),
            "remaining_count": (
                self._work_queue
                .pending_count()
            ),
            "results": results,
            "paper_only": True,
            "live_order_submitted": False,
        }
