import pytest

from core.scanner_health_monitor import ScannerHealthMonitor


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
def monitor(clock):
    return ScannerHealthMonitor(
        heartbeat_timeout_seconds=30,
        max_latency_ms=500,
        clock=clock.now,
    )


def test_records_healthy_scanner_heartbeat(monitor):
    result = monitor.record_heartbeat(
        scanner_id="SCANNER-001",
        latency_ms=120,
        opportunities_found=4,
    )

    assert result["healthy"] is True
    assert result["reason"] is None
    assert result["scanner_id"] == "SCANNER-001"


def test_marks_scanner_degraded_when_latency_exceeds_limit(monitor):
    result = monitor.record_heartbeat(
        scanner_id="SCANNER-002",
        latency_ms=750,
        opportunities_found=1,
    )

    assert result["healthy"] is False
    assert result["reason"] == "latency_exceeded"


def test_detects_stalled_scanner_after_timeout(monitor, clock):
    monitor.record_heartbeat(
        scanner_id="SCANNER-003",
        latency_ms=100,
        opportunities_found=2,
    )

    clock.advance(31)
    result = monitor.check_health("SCANNER-003")

    assert result["healthy"] is False
    assert result["reason"] == "heartbeat_timeout"


def test_reports_scanner_statistics(monitor):
    monitor.record_heartbeat(
        scanner_id="SCANNER-004",
        latency_ms=150,
        opportunities_found=3,
    )
    monitor.record_heartbeat(
        scanner_id="SCANNER-004",
        latency_ms=200,
        opportunities_found=5,
    )

    stats = monitor.statistics("SCANNER-004")

    assert stats["heartbeats"] == 2
    assert stats["opportunities_found"] == 8
    assert stats["average_latency_ms"] == 175.0


def test_missing_scanner_id_is_rejected(monitor):
    with pytest.raises(ValueError, match="scanner_id is required"):
        monitor.record_heartbeat(
            scanner_id="",
            latency_ms=100,
            opportunities_found=1,
        )


def test_negative_latency_is_rejected(monitor):
    with pytest.raises(ValueError, match="latency_ms cannot be negative"):
        monitor.record_heartbeat(
            scanner_id="SCANNER-005",
            latency_ms=-1,
            opportunities_found=1,
        )
