"""
ArbOS™

Persistent Route Worker Pool

Maintains a fixed set of long-lived route worker threads
against the shared route queue, market cache and route
registry.

Unlike ContinuousRouteWorkerPool.run_until_empty(), this
pool is designed for continuously arriving market events.

Paper-safe infrastructure only.
No authentication.
No transfers.
No live orders.
"""

import threading
import time


class PersistentRouteWorkerPool:
    def __init__(
        self,
        worker_count,
        work_queue,
        market_cache,
        route_registry,
        worker_factory,
        idle_sleep_seconds=0.005,
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

        idle_sleep_seconds = float(
            idle_sleep_seconds
        )

        if idle_sleep_seconds <= 0:
            raise ValueError(
                "idle_sleep_seconds must be positive"
            )

        self._worker_count = int(
            worker_count
        )

        self._work_queue = work_queue
        self._market_cache = market_cache
        self._route_registry = route_registry
        self._worker_factory = worker_factory

        self._idle_sleep_seconds = (
            idle_sleep_seconds
        )

        self._stop_event = (
            threading.Event()
        )

        self._state_lock = (
            threading.Lock()
        )

        self._statistics_lock = (
            threading.Lock()
        )

        self._threads = []

        self._running = False

        self._processed_count = 0
        self._idle_polls = 0
        self._worker_errors = []

        self._started_at = None
        self._stopped_at = None

    def start(self):
        with self._state_lock:
            if self._running:
                return {
                    "started": False,
                    "already_running": True,
                    "worker_count": (
                        self._worker_count
                    ),
                    "paper_only": True,
                    "live_order_submitted": False,
                }

            self._stop_event.clear()

            self._threads = []

            self._running = True
            self._started_at = (
                time.perf_counter()
            )
            self._stopped_at = None

            for index in range(
                self._worker_count
            ):
                thread = threading.Thread(
                    target=self._run_worker,
                    args=(index,),
                    name=(
                        "arbos-route-worker-"
                        f"{index}"
                    ),
                    daemon=False,
                )

                self._threads.append(
                    thread
                )

                thread.start()

        return {
            "started": True,
            "already_running": False,
            "worker_count": (
                self._worker_count
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def _run_worker(
        self,
        worker_index,
    ):
        worker = self._worker_factory(
            work_queue=self._work_queue,
            market_cache=self._market_cache,
            route_registry=(
                self._route_registry
            ),
        )

        while not self._stop_event.is_set():
            try:
                result = worker.process_next()

            except Exception as exc:
                with self._statistics_lock:
                    self._worker_errors.append({
                        "worker_index": (
                            worker_index
                        ),
                        "error_type": (
                            type(exc).__name__
                        ),
                        "error": str(exc),
                    })

                time.sleep(
                    self._idle_sleep_seconds
                )
                continue

            if result is None:
                with self._statistics_lock:
                    self._idle_polls += 1

                time.sleep(
                    self._idle_sleep_seconds
                )
                continue

            with self._statistics_lock:
                self._processed_count += 1

    def stop(
        self,
        join_timeout_seconds=10.0,
    ):
        join_timeout_seconds = float(
            join_timeout_seconds
        )

        if join_timeout_seconds <= 0:
            raise ValueError(
                "join_timeout_seconds must be positive"
            )

        with self._state_lock:
            if not self._running:
                return {
                    "stopped": False,
                    "already_stopped": True,
                    "worker_count": (
                        self._worker_count
                    ),
                    "alive_thread_count": sum(
                        thread.is_alive()
                        for thread
                        in self._threads
                    ),
                    "paper_only": True,
                    "live_order_submitted": False,
                }

            self._stop_event.set()

            threads = list(
                self._threads
            )

        deadline = (
            time.monotonic()
            + join_timeout_seconds
        )

        for thread in threads:
            remaining = (
                deadline
                - time.monotonic()
            )

            if remaining <= 0:
                break

            thread.join(
                timeout=remaining
            )

        alive_thread_count = sum(
            thread.is_alive()
            for thread in threads
        )

        with self._state_lock:
            self._running = False
            self._stopped_at = (
                time.perf_counter()
            )

        return {
            "stopped": (
                alive_thread_count == 0
            ),
            "already_stopped": False,
            "worker_count": (
                self._worker_count
            ),
            "alive_thread_count": (
                alive_thread_count
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def is_running(self):
        with self._state_lock:
            return bool(
                self._running
            )

    def statistics(self):
        with self._statistics_lock:
            processed_count = int(
                self._processed_count
            )

            idle_polls = int(
                self._idle_polls
            )

            worker_errors = [
                dict(item)
                for item
                in self._worker_errors
            ]

        alive_thread_count = sum(
            thread.is_alive()
            for thread in self._threads
        )

        now = time.perf_counter()

        if self._started_at is None:
            elapsed_seconds = 0.0

        elif self._stopped_at is not None:
            elapsed_seconds = (
                self._stopped_at
                - self._started_at
            )

        else:
            elapsed_seconds = (
                now
                - self._started_at
            )

        routes_per_second = (
            processed_count
            / elapsed_seconds
            if elapsed_seconds > 0
            else 0.0
        )

        return {
            "worker_count": (
                self._worker_count
            ),
            "running": (
                self.is_running()
            ),
            "alive_thread_count": (
                alive_thread_count
            ),
            "processed_count": (
                processed_count
            ),
            "idle_polls": idle_polls,
            "pending_count": (
                self._work_queue
                .pending_count()
            ),
            "elapsed_seconds": round(
                elapsed_seconds,
                6,
            ),
            "routes_per_second": round(
                routes_per_second,
                3,
            ),
            "worker_error_count": len(
                worker_errors
            ),
            "worker_errors": (
                worker_errors
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
