import pytest

from core.execution_circuit_breaker import ExecutionCircuitBreaker


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
def breaker(clock):
    return ExecutionCircuitBreaker(
        failure_threshold=3,
        recovery_timeout_seconds=30,
        clock=clock.now,
    )


def test_starts_closed(breaker):
    result = breaker.status()

    assert result["state"] == "CLOSED"
    assert result["failure_count"] == 0


def test_opens_after_failure_threshold(breaker):
    breaker.record_failure("network_error")
    breaker.record_failure("exchange_error")
    result = breaker.record_failure("timeout")

    assert result["state"] == "OPEN"
    assert result["failure_count"] == 3
    assert result["allowed"] is False


def test_open_circuit_blocks_execution(breaker):
    breaker.record_failure("one")
    breaker.record_failure("two")
    breaker.record_failure("three")

    result = breaker.allow_execution()

    assert result["allowed"] is False
    assert result["state"] == "OPEN"
    assert result["reason"] == "circuit_open"


def test_moves_to_half_open_after_recovery_timeout(breaker, clock):
    breaker.record_failure("one")
    breaker.record_failure("two")
    breaker.record_failure("three")
    clock.advance(30)

    result = breaker.allow_execution()

    assert result["allowed"] is True
    assert result["state"] == "HALF_OPEN"
    assert result["reason"] is None


def test_success_closes_half_open_circuit(breaker, clock):
    breaker.record_failure("one")
    breaker.record_failure("two")
    breaker.record_failure("three")
    clock.advance(30)
    breaker.allow_execution()

    result = breaker.record_success()

    assert result["state"] == "CLOSED"
    assert result["failure_count"] == 0
    assert result["allowed"] is True


def test_failure_reopens_half_open_circuit(breaker, clock):
    breaker.record_failure("one")
    breaker.record_failure("two")
    breaker.record_failure("three")
    clock.advance(30)
    breaker.allow_execution()

    result = breaker.record_failure("test_failed")

    assert result["state"] == "OPEN"
    assert result["allowed"] is False


def test_invalid_failure_threshold_is_rejected(clock):
    with pytest.raises(ValueError, match="failure_threshold must be positive"):
        ExecutionCircuitBreaker(
            failure_threshold=0,
            recovery_timeout_seconds=30,
            clock=clock.now,
        )


def test_negative_recovery_timeout_is_rejected(clock):
    with pytest.raises(ValueError, match="recovery_timeout_seconds cannot be negative"):
        ExecutionCircuitBreaker(
            failure_threshold=3,
            recovery_timeout_seconds=-1,
            clock=clock.now,
        )
