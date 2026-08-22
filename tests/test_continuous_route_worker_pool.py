import threading
import time

from core.continuous_route_worker_pool import (
    ContinuousRouteWorkerPool,
)


class FakeQueue:
    def __init__(self, items):
        self._items = list(items)
        self._lock = threading.Lock()

    def dequeue(self):
        with self._lock:
            if not self._items:
                return None

            return self._items.pop(0)

    def pending_count(self):
        with self._lock:
            return len(self._items)


class FakeWorker:
    def __init__(
        self,
        work_queue,
        market_cache,
        route_registry,
    ):
        self._queue = work_queue

    def process_next(self):
        item = self._queue.dequeue()

        if item is None:
            return None

        time.sleep(0.01)

        return {
            "processed": True,
            "route_id": item["route_id"],
            "paper_only": True,
            "live_order_submitted": False,
        }


def work_items(count):
    return [
        {
            "request_id": f"REQ-{index}",
            "route_id": f"R{index}",
            "sequence": index,
        }
        for index in range(count)
    ]


def test_pool_processes_all_available_work():
    queue = FakeQueue(
        work_items(20)
    )

    pool = ContinuousRouteWorkerPool(
        worker_count=4,
        work_queue=queue,
        market_cache=object(),
        route_registry=object(),
        worker_factory=FakeWorker,
    )

    result = pool.run_until_empty()

    assert result["processed_count"] == 20
    assert result["remaining_count"] == 0
    assert len(result["results"]) == 20


def test_multiple_workers_process_in_parallel():
    class ConcurrencyWorker:
        active = 0
        max_active = 0
        lock = threading.Lock()
        release = threading.Event()
        four_active = threading.Event()

        def __init__(
            self,
            work_queue,
            market_cache,
            route_registry,
        ):
            self._queue = work_queue

        def process_next(self):
            item = self._queue.dequeue()

            if item is None:
                return None

            with self.lock:
                type(self).active += 1
                type(self).max_active = max(
                    type(self).max_active,
                    type(self).active,
                )

                if type(self).active >= 4:
                    type(self).four_active.set()

            try:
                type(self).release.wait(
                    timeout=1.0
                )
            finally:
                with self.lock:
                    type(self).active -= 1

            return {
                "processed": True,
                "route_id": item["route_id"],
                "paper_only": True,
                "live_order_submitted": False,
            }

    queue = FakeQueue(
        work_items(8)
    )

    pool = ContinuousRouteWorkerPool(
        worker_count=4,
        work_queue=queue,
        market_cache=object(),
        route_registry=object(),
        worker_factory=ConcurrencyWorker,
    )

    result_holder = {}

    def run_pool():
        result_holder["result"] = (
            pool.run_until_empty()
        )

    runner = threading.Thread(
        target=run_pool
    )

    runner.start()

    assert ConcurrencyWorker.four_active.wait(
        timeout=1.0
    )

    assert ConcurrencyWorker.max_active == 4

    ConcurrencyWorker.release.set()

    runner.join(
        timeout=2.0
    )

    assert not runner.is_alive()

    result = result_holder["result"]

    assert result["processed_count"] == 8


def test_each_route_is_processed_once():
    queue = FakeQueue(
        work_items(50)
    )

    pool = ContinuousRouteWorkerPool(
        worker_count=8,
        work_queue=queue,
        market_cache=object(),
        route_registry=object(),
        worker_factory=FakeWorker,
    )

    result = pool.run_until_empty()

    route_ids = [
        item["route_id"]
        for item in result["results"]
    ]

    assert len(route_ids) == 50
    assert len(set(route_ids)) == 50


def test_pool_reports_worker_count():
    pool = ContinuousRouteWorkerPool(
        worker_count=6,
        work_queue=FakeQueue([]),
        market_cache=object(),
        route_registry=object(),
        worker_factory=FakeWorker,
    )

    result = pool.run_until_empty()

    assert result["worker_count"] == 6


def test_pool_is_paper_safe():
    pool = ContinuousRouteWorkerPool(
        worker_count=2,
        work_queue=FakeQueue(
            work_items(2)
        ),
        market_cache=object(),
        route_registry=object(),
        worker_factory=FakeWorker,
    )

    result = pool.run_until_empty()

    assert result["paper_only"] is True
    assert result[
        "live_order_submitted"
    ] is False


def test_worker_count_must_be_positive():
    try:
        ContinuousRouteWorkerPool(
            worker_count=0,
            work_queue=FakeQueue([]),
            market_cache=object(),
            route_registry=object(),
            worker_factory=FakeWorker,
        )
    except ValueError as exc:
        assert str(exc) == (
            "worker_count must be positive"
        )
    else:
        raise AssertionError(
            "expected ValueError"
        )


def test_bounded_pool_processes_at_most_max_items():
    queue = FakeQueue(
        work_items(50)
    )

    pool = ContinuousRouteWorkerPool(
        worker_count=4,
        work_queue=queue,
        market_cache=object(),
        route_registry=object(),
        worker_factory=FakeWorker,
    )

    result = pool.run_until_empty(
        max_items=12
    )

    assert result["processed_count"] == 12
    assert result["remaining_count"] == 38


def test_bounded_pool_can_continue_in_later_cycle():
    queue = FakeQueue(
        work_items(20)
    )

    pool = ContinuousRouteWorkerPool(
        worker_count=4,
        work_queue=queue,
        market_cache=object(),
        route_registry=object(),
        worker_factory=FakeWorker,
    )

    first = pool.run_until_empty(
        max_items=8
    )

    second = pool.run_until_empty(
        max_items=8
    )

    third = pool.run_until_empty(
        max_items=8
    )

    assert first["processed_count"] == 8
    assert second["processed_count"] == 8
    assert third["processed_count"] == 4
    assert third["remaining_count"] == 0


def test_max_items_must_be_positive():
    pool = ContinuousRouteWorkerPool(
        worker_count=2,
        work_queue=FakeQueue([]),
        market_cache=object(),
        route_registry=object(),
        worker_factory=FakeWorker,
    )

    try:
        pool.run_until_empty(
            max_items=0
        )
    except ValueError as exc:
        assert str(exc) == (
            "max_items must be positive"
        )
    else:
        raise AssertionError(
            "expected ValueError"
        )
