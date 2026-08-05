import pytest

from core.exchange_connectivity_supervisor import (
    ExchangeConnectivitySupervisor,
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
def supervisor(clock):
    return ExchangeConnectivitySupervisor(
        disconnect_timeout_seconds=30,
        max_latency_ms=1000,
        clock=clock.now,
    )


def test_records_healthy_exchange_heartbeat(supervisor):
    result = supervisor.record_heartbeat(
        exchange_id="kraken",
        latency_ms=250,
        connected=True,
    )

    assert result["healthy"] is True
    assert result["reason"] is None
    assert result["exchange_id"] == "kraken"


def test_marks_exchange_degraded_when_latency_exceeds_limit(supervisor):
    result = supervisor.record_heartbeat(
        exchange_id="kraken",
        latency_ms=1500,
        connected=True,
    )

    assert result["healthy"] is False
    assert result["reason"] == "latency_exceeded"


def test_marks_exchange_disconnected(supervisor):
    result = supervisor.record_heartbeat(
        exchange_id="kraken",
        latency_ms=250,
        connected=False,
    )

    assert result["healthy"] is False
    assert result["reason"] == "exchange_disconnected"


def test_detects_exchange_timeout(supervisor, clock):
    supervisor.record_heartbeat(
        exchange_id="kraken",
        latency_ms=250,
        connected=True,
    )

    clock.advance(31)
    result = supervisor.check_health("kraken")

    assert result["healthy"] is False
    assert result["reason"] == "connection_timeout"


def test_missing_exchange_id_is_rejected(supervisor):
    with pytest.raises(ValueError, match="exchange_id is required"):
        supervisor.record_heartbeat(
            exchange_id="",
            latency_ms=100,
            connected=True,
        )


def test_negative_latency_is_rejected(supervisor):
    with pytest.raises(ValueError, match="latency_ms cannot be negative"):
        supervisor.record_heartbeat(
            exchange_id="kraken",
            latency_ms=-1,
            connected=True,
        )
