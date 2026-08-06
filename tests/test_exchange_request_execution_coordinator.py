import pytest

from core.exchange_request_queue_manager import ExchangeRequestQueueManager
from core.exchange_rate_limiter import ExchangeRateLimiter
from core.exchange_connectivity_supervisor import ExchangeConnectivitySupervisor
from core.execution_circuit_breaker import ExecutionCircuitBreaker
from core.exchange_request_execution_coordinator import (
    ExchangeRequestExecutionCoordinator,
)


class FakeClock:
    def __init__(self):
        self.value = 1000.0

    def now(self):
        return self.value


class FakeDispatcher:
    def __init__(self):
        self.requests = []
        self.succeed = True

    def execute(self, request):
        self.requests.append(dict(request))
        return {
            "success": self.succeed,
            "request_id": request["request_id"],
        }


@pytest.fixture
def setup_system():
    clock = FakeClock()
    queue = ExchangeRequestQueueManager(max_queue_size=10, clock=clock.now)
    limiter = ExchangeRateLimiter(
        max_requests=3,
        window_seconds=10,
        clock=clock.now,
    )
    connectivity = ExchangeConnectivitySupervisor(
        disconnect_timeout_seconds=30,
        max_latency_ms=1000,
        clock=clock.now,
    )
    breaker = ExecutionCircuitBreaker(
        failure_threshold=3,
        recovery_timeout_seconds=30,
        clock=clock.now,
    )
    dispatcher = FakeDispatcher()

    connectivity.record_heartbeat(
        exchange_id="kraken",
        latency_ms=100,
        connected=True,
    )

    coordinator = ExchangeRequestExecutionCoordinator(
        queue_manager=queue,
        rate_limiter=limiter,
        connectivity_supervisor=connectivity,
        circuit_breaker=breaker,
        dispatcher=dispatcher,
    )

    return {
        "clock": clock,
        "queue": queue,
        "limiter": limiter,
        "connectivity": connectivity,
        "breaker": breaker,
        "dispatcher": dispatcher,
        "coordinator": coordinator,
    }


def test_executes_request_when_all_controls_allow(setup_system):
    queue = setup_system["queue"]
    coordinator = setup_system["coordinator"]

    queue.enqueue({
        "request_id": "REQ-001",
        "exchange_id": "kraken",
        "operation": "fetch_balance",
        "priority": 1,
    })

    result = coordinator.process_next()

    assert result["processed"] is True
    assert result["success"] is True
    assert result["request_id"] == "REQ-001"


def test_requeues_request_when_exchange_unhealthy(setup_system):
    queue = setup_system["queue"]
    connectivity = setup_system["connectivity"]
    coordinator = setup_system["coordinator"]

    connectivity.record_heartbeat(
        exchange_id="kraken",
        latency_ms=100,
        connected=False,
    )

    queue.enqueue({
        "request_id": "REQ-002",
        "exchange_id": "kraken",
        "operation": "fetch_balance",
        "priority": 1,
    })

    result = coordinator.process_next()

    assert result["processed"] is False
    assert result["reason"] == "exchange_disconnected"
    assert queue.pending_count() == 1


def test_requeues_request_when_circuit_is_open(setup_system):
    queue = setup_system["queue"]
    breaker = setup_system["breaker"]
    coordinator = setup_system["coordinator"]

    breaker.record_failure("one")
    breaker.record_failure("two")
    breaker.record_failure("three")

    queue.enqueue({
        "request_id": "REQ-003",
        "exchange_id": "kraken",
        "operation": "fetch_balance",
        "priority": 1,
    })

    result = coordinator.process_next()

    assert result["processed"] is False
    assert result["reason"] == "circuit_open"
    assert queue.pending_count() == 1


def test_requeues_request_when_rate_limited(setup_system):
    queue = setup_system["queue"]
    limiter = setup_system["limiter"]
    coordinator = setup_system["coordinator"]

    limiter.allow_request("kraken")
    limiter.allow_request("kraken")
    limiter.allow_request("kraken")

    queue.enqueue({
        "request_id": "REQ-004",
        "exchange_id": "kraken",
        "operation": "fetch_balance",
        "priority": 1,
    })

    result = coordinator.process_next()

    assert result["processed"] is False
    assert result["reason"] == "rate_limit_reached"
    assert queue.pending_count() == 1


def test_dispatch_failure_records_circuit_failure(setup_system):
    queue = setup_system["queue"]
    dispatcher = setup_system["dispatcher"]
    breaker = setup_system["breaker"]
    coordinator = setup_system["coordinator"]

    dispatcher.succeed = False

    queue.enqueue({
        "request_id": "REQ-005",
        "exchange_id": "kraken",
        "operation": "fetch_balance",
        "priority": 1,
    })

    result = coordinator.process_next()

    assert result["processed"] is True
    assert result["success"] is False
    assert breaker.status()["failure_count"] == 1


def test_dispatch_success_records_circuit_success(setup_system):
    queue = setup_system["queue"]
    breaker = setup_system["breaker"]
    coordinator = setup_system["coordinator"]

    breaker.record_failure("temporary")

    queue.enqueue({
        "request_id": "REQ-006",
        "exchange_id": "kraken",
        "operation": "fetch_balance",
        "priority": 1,
    })

    result = coordinator.process_next()

    assert result["success"] is True
    assert breaker.status()["failure_count"] == 0
    assert breaker.status()["state"] == "CLOSED"


def test_returns_none_when_queue_is_empty(setup_system):
    coordinator = setup_system["coordinator"]

    assert coordinator.process_next() is None
