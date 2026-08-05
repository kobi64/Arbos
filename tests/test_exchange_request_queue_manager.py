import pytest

from core.exchange_request_queue_manager import (
    ExchangeRequestQueueManager,
)


class FakeClock:
    def __init__(self):
        self.value = 1000.0

    def now(self):
        return self.value

    def advance(self, seconds):
        self.value += seconds


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def manager(clock):
    return ExchangeRequestQueueManager(
        max_queue_size=5,
        clock=clock.now,
    )


def test_enqueues_request(manager):
    result = manager.enqueue({
        "request_id": "REQ-001",
        "exchange_id": "kraken",
        "operation": "fetch_balance",
        "priority": 1,
    })

    assert result["queued"] is True
    assert result["request_id"] == "REQ-001"
    assert manager.pending_count() == 1


def test_processes_highest_priority_first(manager):
    manager.enqueue({
        "request_id": "REQ-LOW",
        "exchange_id": "kraken",
        "operation": "fetch_balance",
        "priority": 1,
    })
    manager.enqueue({
        "request_id": "REQ-HIGH",
        "exchange_id": "kraken",
        "operation": "cancel_order",
        "priority": 10,
    })

    result = manager.dequeue()

    assert result["request_id"] == "REQ-HIGH"
    assert manager.pending_count() == 1


def test_preserves_fifo_for_equal_priority(manager):
    manager.enqueue({
        "request_id": "REQ-001",
        "exchange_id": "kraken",
        "operation": "fetch_balance",
        "priority": 5,
    })
    manager.enqueue({
        "request_id": "REQ-002",
        "exchange_id": "kraken",
        "operation": "fetch_ticker",
        "priority": 5,
    })

    first = manager.dequeue()
    second = manager.dequeue()

    assert first["request_id"] == "REQ-001"
    assert second["request_id"] == "REQ-002"


def test_preserves_fifo_for_equal_priority(manager):
    manager.enqueue({
        "request_id": "REQ-001",
        "exchange_id": "kraken",
        "operation": "fetch_balance",
        "priority": 5,
    })
    manager.enqueue({
        "request_id": "REQ-002",
        "exchange_id": "kraken",
        "operation": "fetch_ticker",
        "priority": 5,
    })

    first = manager.dequeue()
    second = manager.dequeue()

    assert first["request_id"] == "REQ-001"
    assert second["request_id"] == "REQ-002"


def test_rejects_request_when_queue_is_full(manager):
    for index in range(5):
        manager.enqueue({
            "request_id": f"REQ-{index}",
            "exchange_id": "kraken",
            "operation": "fetch_balance",
            "priority": 1,
        })

    result = manager.enqueue({
        "request_id": "REQ-OVERFLOW",
        "exchange_id": "kraken",
        "operation": "fetch_balance",
        "priority": 1,
    })

    assert result["queued"] is False
    assert result["reason"] == "queue_full"


def test_missing_request_id_is_rejected(manager):
    with pytest.raises(ValueError, match="request_id is required"):
        manager.enqueue({
            "exchange_id": "kraken",
            "operation": "fetch_balance",
            "priority": 1,
        })


def test_invalid_max_queue_size_is_rejected(clock):
    with pytest.raises(ValueError, match="max_queue_size must be positive"):
        ExchangeRequestQueueManager(
            max_queue_size=0,
            clock=clock.now,
        )
