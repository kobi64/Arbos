import threading
import time

import pytest

from core.persistent_route_worker_pool import (
    PersistentRouteWorkerPool,
)


class FakeQueue:
    def __init__(
        self,
        items=None,
    ):
        self._items = list(
            items or []
        )

        self._lock = (
            threading.Lock()
        )

    def enqueue(
        self,
        item,
    ):
        with self._lock:
            self._items.append(
                dict(item)
            )

    def dequeue(self):
        with self._lock:
            if not self._items:
                return None

            return self._items.pop(0)

    def pending_count(self):
        with self._lock:
            return len(
                self._items
            )


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

        return {
            "processed": True,
            "route_id": (
                item["route_id"]
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }


class FailingWorker:
    calls = 0

    def __init__(
        self,
        work_queue,
        market_cache,
        route_registry,
    ):
        self._queue = work_queue

    def process_next(self):
        type(self).calls += 1

        if type(self).calls == 1:
            raise RuntimeError(
                "temporary worker failure"
            )

        item = self._queue.dequeue()

        if item is None:
            return None

        return {
            "processed": True,
            "route_id": (
                item["route_id"]
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }


def work_items(
    count,
):
    return [
        {
            "route_id": (
                f"R-{index}"
            )
        }
        for index in range(
            count
        )
    ]


def wait_until(
    predicate,
    timeout=2.0,
):
    deadline = (
        time.monotonic()
        + timeout
    )

    while (
        time.monotonic()
        < deadline
    ):
        if predicate():
            return True

        time.sleep(
            0.005
        )

    return False


def test_persistent_pool_processes_existing_work():
    queue = FakeQueue(
        work_items(100)
    )

    pool = PersistentRouteWorkerPool(
        worker_count=4,
        work_queue=queue,
        market_cache=object(),
        route_registry=object(),
        worker_factory=FakeWorker,
    )

    result = pool.start()

    assert result["started"] is True

    assert wait_until(
        lambda: (
            queue.pending_count()
            == 0
        )
    )

    stopped = pool.stop()

    assert stopped["stopped"] is True

    stats = pool.statistics()

    assert (
        stats["processed_count"]
        == 100
    )

    assert stats[
        "alive_thread_count"
    ] == 0

    assert stats[
        "live_order_submitted"
    ] is False


def test_persistent_pool_processes_work_arriving_later():
    queue = FakeQueue()

    pool = PersistentRouteWorkerPool(
        worker_count=2,
        work_queue=queue,
        market_cache=object(),
        route_registry=object(),
        worker_factory=FakeWorker,
    )

    pool.start()

    time.sleep(
        0.02
    )

    for item in work_items(25):
        queue.enqueue(
            item
        )

    assert wait_until(
        lambda: (
            pool.statistics()[
                "processed_count"
            ]
            >= 25
        )
    )

    result = pool.stop()

    assert result["stopped"] is True
    assert queue.pending_count() == 0


def test_start_is_idempotent():
    pool = PersistentRouteWorkerPool(
        worker_count=2,
        work_queue=FakeQueue(),
        market_cache=object(),
        route_registry=object(),
        worker_factory=FakeWorker,
    )

    first = pool.start()
    second = pool.start()

    assert first["started"] is True
    assert second["started"] is False
    assert second[
        "already_running"
    ] is True

    pool.stop()


def test_stop_is_idempotent():
    pool = PersistentRouteWorkerPool(
        worker_count=2,
        work_queue=FakeQueue(),
        market_cache=object(),
        route_registry=object(),
        worker_factory=FakeWorker,
    )

    pool.start()

    first = pool.stop()
    second = pool.stop()

    assert first["stopped"] is True
    assert second["stopped"] is False
    assert second[
        "already_stopped"
    ] is True


def test_worker_error_does_not_kill_pool():
    FailingWorker.calls = 0

    queue = FakeQueue(
        work_items(5)
    )

    pool = PersistentRouteWorkerPool(
        worker_count=1,
        work_queue=queue,
        market_cache=object(),
        route_registry=object(),
        worker_factory=FailingWorker,
        idle_sleep_seconds=0.001,
    )

    pool.start()

    assert wait_until(
        lambda: (
            queue.pending_count()
            == 0
        )
    )

    pool.stop()

    stats = pool.statistics()

    assert stats[
        "processed_count"
    ] == 5

    assert stats[
        "worker_error_count"
    ] == 1


def test_statistics_report_throughput():
    queue = FakeQueue(
        work_items(20)
    )

    pool = PersistentRouteWorkerPool(
        worker_count=2,
        work_queue=queue,
        market_cache=object(),
        route_registry=object(),
        worker_factory=FakeWorker,
    )

    pool.start()

    assert wait_until(
        lambda: (
            queue.pending_count()
            == 0
        )
    )

    pool.stop()

    stats = pool.statistics()

    assert stats[
        "routes_per_second"
    ] > 0

    assert stats[
        "processed_count"
    ] == 20


@pytest.mark.parametrize(
    "worker_count",
    [
        0,
        -1,
    ],
)
def test_worker_count_must_be_positive(
    worker_count,
):
    with pytest.raises(
        ValueError,
        match=(
            "worker_count must be positive"
        ),
    ):
        PersistentRouteWorkerPool(
            worker_count=worker_count,
            work_queue=FakeQueue(),
            market_cache=object(),
            route_registry=object(),
            worker_factory=FakeWorker,
        )


def test_idle_sleep_must_be_positive():
    with pytest.raises(
        ValueError,
        match=(
            "idle_sleep_seconds must be positive"
        ),
    ):
        PersistentRouteWorkerPool(
            worker_count=1,
            work_queue=FakeQueue(),
            market_cache=object(),
            route_registry=object(),
            worker_factory=FakeWorker,
            idle_sleep_seconds=0,
        )


def test_persistent_pool_is_paper_safe():
    pool = PersistentRouteWorkerPool(
        worker_count=1,
        work_queue=FakeQueue(),
        market_cache=object(),
        route_registry=object(),
        worker_factory=FakeWorker,
    )

    started = pool.start()
    stopped = pool.stop()
    stats = pool.statistics()

    assert started[
        "paper_only"
    ] is True

    assert stopped[
        "paper_only"
    ] is True

    assert stats[
        "paper_only"
    ] is True

    assert started[
        "live_order_submitted"
    ] is False

    assert stopped[
        "live_order_submitted"
    ] is False

    assert stats[
        "live_order_submitted"
    ] is False
