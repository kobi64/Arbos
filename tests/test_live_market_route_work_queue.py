import pytest

from core.live_market_route_work_queue import (
    LiveMarketRouteWorkQueue,
)


def request(
    route_id,
    sequence,
    priority=1.0,
):
    return {
        "request_id": (
            f"REQ-{route_id}-{sequence}"
        ),
        "route_id": route_id,
        "exchange_id": "kucoin",
        "symbol": "BTC/USDT",
        "sequence": sequence,
        "priority": priority,
        "paper_only": True,
        "live_order_submitted": False,
    }


def test_enqueues_new_route_work():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=10
    )

    result = queue.enqueue(
        request("R1", 100)
    )

    assert result["queued"] is True
    assert result["coalesced"] is False
    assert queue.pending_count() == 1


def test_newer_event_coalesces_existing_route_work():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=10
    )

    queue.enqueue(
        request("R1", 100)
    )

    result = queue.enqueue(
        request("R1", 101)
    )

    assert result["queued"] is True
    assert result["coalesced"] is True

    assert queue.pending_count() == 1

    item = queue.dequeue()

    assert item["route_id"] == "R1"
    assert item["sequence"] == 101


def test_multiple_newer_updates_keep_only_latest():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=10
    )

    queue.enqueue(
        request("R1", 100)
    )

    queue.enqueue(
        request("R1", 101)
    )

    queue.enqueue(
        request("R1", 102)
    )

    assert queue.pending_count() == 1

    item = queue.dequeue()

    assert item["sequence"] == 102


def test_stale_event_is_rejected():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=10
    )

    queue.enqueue(
        request("R1", 105)
    )

    result = queue.enqueue(
        request("R1", 104)
    )

    assert result["queued"] is False
    assert result["reason"] == (
        "stale_route_event"
    )

    assert queue.pending_count() == 1

    item = queue.dequeue()

    assert item["sequence"] == 105


def test_same_sequence_is_not_queued_twice():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=10
    )

    queue.enqueue(
        request("R1", 100)
    )

    result = queue.enqueue(
        request("R1", 100)
    )

    assert result["queued"] is False
    assert result["reason"] == (
        "duplicate_route_event"
    )

    assert queue.pending_count() == 1


def test_different_routes_remain_independent():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=10
    )

    queue.enqueue(
        request("R1", 100)
    )

    queue.enqueue(
        request("R2", 100)
    )

    assert queue.pending_count() == 2


def test_highest_priority_route_is_processed_first():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=10
    )

    queue.enqueue(
        request(
            "R-LOW",
            100,
            priority=1.0,
        )
    )

    queue.enqueue(
        request(
            "R-HIGH",
            100,
            priority=10.0,
        )
    )

    result = queue.dequeue()

    assert result["route_id"] == (
        "R-HIGH"
    )


def test_coalesced_update_can_raise_route_priority():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=10
    )

    queue.enqueue(
        request(
            "R1",
            100,
            priority=1.0,
        )
    )

    queue.enqueue(
        request(
            "R2",
            100,
            priority=5.0,
        )
    )

    queue.enqueue(
        request(
            "R1",
            101,
            priority=10.0,
        )
    )

    result = queue.dequeue()

    assert result["route_id"] == "R1"
    assert result["sequence"] == 101
    assert result["priority"] == 10.0


def test_queue_capacity_counts_active_routes_not_obsolete_updates():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=2
    )

    queue.enqueue(
        request("R1", 100)
    )

    queue.enqueue(
        request("R1", 101)
    )

    queue.enqueue(
        request("R1", 102)
    )

    assert queue.pending_count() == 1

    result = queue.enqueue(
        request("R2", 100)
    )

    assert result["queued"] is True
    assert queue.pending_count() == 2


def test_rejects_new_route_when_queue_is_full():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=1
    )

    queue.enqueue(
        request("R1", 100)
    )

    result = queue.enqueue(
        request("R2", 100)
    )

    assert result["queued"] is False
    assert result["reason"] == "queue_full"


def test_route_id_is_required():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=10
    )

    with pytest.raises(
        ValueError,
        match="route_id is required",
    ):
        queue.enqueue({
            "request_id": "REQ",
            "sequence": 1,
        })


def test_positive_queue_size_is_required():
    with pytest.raises(
        ValueError,
        match=(
            "max_queue_size must be positive"
        ),
    ):
        LiveMarketRouteWorkQueue(
            max_queue_size=0
        )


import threading


def test_concurrent_enqueue_keeps_one_latest_item_per_route():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=100
    )

    barrier = threading.Barrier(20)

    def producer(sequence):
        barrier.wait()

        queue.enqueue({
            "request_id": (
                f"REQ-R1-{sequence}"
            ),
            "route_id": "R1",
            "exchange_id": "kucoin",
            "symbol": "BTC/USDT",
            "sequence": sequence,
            "priority": float(sequence),
        })

    threads = [
        threading.Thread(
            target=producer,
            args=(sequence,),
        )
        for sequence in range(
            100,
            120,
        )
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert queue.pending_count() == 1

    item = queue.dequeue()

    assert item["route_id"] == "R1"
    assert item["sequence"] == 119


def test_concurrent_dequeue_returns_each_route_at_most_once():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=100
    )

    route_count = 20

    for index in range(route_count):
        queue.enqueue({
            "request_id": (
                f"REQ-R{index}"
            ),
            "route_id": (
                f"R{index}"
            ),
            "sequence": 1,
            "priority": 1.0,
        })

    results = []
    results_lock = threading.Lock()

    def consumer():
        item = queue.dequeue()

        if item is not None:
            with results_lock:
                results.append(
                    item["route_id"]
                )

    threads = [
        threading.Thread(
            target=consumer
        )
        for _ in range(
            route_count
        )
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert len(results) == route_count

    assert len(
        set(results)
    ) == route_count

    assert queue.pending_count() == 0
