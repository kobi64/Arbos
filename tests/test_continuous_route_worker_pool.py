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
    queue = FakeQueue(
        work_items(8)
    )

    pool = ContinuousRouteWorkerPool(
        worker_count=4,
        work_queue=queue,
        market_cache=object(),
        route_registry=object(),
        worker_factory=FakeWorker,
    )

    started = time.perf_counter()

    result = pool.run_until_empty()

    elapsed = (
        time.perf_counter()
        - started
    )

    assert result["processed_count"] == 8

    assert elapsed < 0.07


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
