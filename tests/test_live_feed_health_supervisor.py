import pytest

from core.live_feed_health_supervisor import (
    LiveFeedHealthSupervisor,
)


class FakeScannerHealth:
    def __init__(self):
        self.heartbeats = []
        self.health = {}

    def record_heartbeat(
        self,
        scanner_id,
        latency_ms,
        opportunities_found,
    ):
        self.heartbeats.append({
            "scanner_id": scanner_id,
            "latency_ms": latency_ms,
            "opportunities_found": opportunities_found,
        })

        result = self.health.get(
            scanner_id,
            {
                "scanner_id": scanner_id,
                "healthy": True,
                "reason": None,
            },
        )

        return dict(result)

    def check_health(
        self,
        scanner_id,
    ):
        return dict(
            self.health.get(
                scanner_id,
                {
                    "scanner_id": scanner_id,
                    "healthy": True,
                    "reason": None,
                },
            )
        )


class FakeConnectivity:
    def __init__(self):
        self.heartbeats = []
        self.health = {}

    def record_heartbeat(
        self,
        exchange_id,
        latency_ms,
        connected,
    ):
        self.heartbeats.append({
            "exchange_id": exchange_id,
            "latency_ms": latency_ms,
            "connected": connected,
        })

        return dict(
            self.health.get(
                exchange_id,
                {
                    "exchange_id": exchange_id,
                    "healthy": connected,
                    "reason": (
                        None
                        if connected
                        else "exchange_disconnected"
                    ),
                },
            )
        )

    def check_health(
        self,
        exchange_id,
    ):
        return dict(
            self.health.get(
                exchange_id,
                {
                    "exchange_id": exchange_id,
                    "healthy": True,
                    "reason": None,
                },
            )
        )


def test_records_successful_symbol_heartbeat():
    scanner = FakeScannerHealth()
    connectivity = FakeConnectivity()

    supervisor = LiveFeedHealthSupervisor(
        scanner_health_monitor=scanner,
        connectivity_supervisor=connectivity,
    )

    result = supervisor.record_success(
        exchange_id="kucoin",
        symbol="BTC/USDT",
        latency_ms=25.0,
    )

    assert result["healthy"] is True

    assert scanner.heartbeats[0][
        "scanner_id"
    ] == "kucoin:BTC/USDT"

    assert connectivity.heartbeats[0] == {
        "exchange_id": "kucoin",
        "latency_ms": 25.0,
        "connected": True,
    }


def test_records_feed_failure_as_disconnected_exchange_heartbeat():
    scanner = FakeScannerHealth()
    connectivity = FakeConnectivity()

    supervisor = LiveFeedHealthSupervisor(
        scanner_health_monitor=scanner,
        connectivity_supervisor=connectivity,
    )

    result = supervisor.record_failure(
        exchange_id="gate",
        symbol="ETH/USDT",
        latency_ms=100.0,
        reason="NETWORK_ERROR",
    )

    assert result["healthy"] is False
    assert result["reason"] == "NETWORK_ERROR"

    assert connectivity.heartbeats[0][
        "connected"
    ] is False


def test_symbol_health_combines_symbol_and_exchange_health():
    scanner = FakeScannerHealth()
    connectivity = FakeConnectivity()

    scanner.health[
        "kucoin:BTC/USDT"
    ] = {
        "scanner_id": "kucoin:BTC/USDT",
        "healthy": True,
        "reason": None,
    }

    connectivity.health[
        "kucoin"
    ] = {
        "exchange_id": "kucoin",
        "healthy": False,
        "reason": "connection_timeout",
    }

    supervisor = LiveFeedHealthSupervisor(
        scanner_health_monitor=scanner,
        connectivity_supervisor=connectivity,
    )

    result = supervisor.check_symbol(
        exchange_id="kucoin",
        symbol="BTC/USDT",
    )

    assert result["healthy"] is False
    assert result["reason"] == (
        "connection_timeout"
    )


def test_symbol_health_reports_scanner_failure():
    scanner = FakeScannerHealth()
    connectivity = FakeConnectivity()

    scanner.health[
        "htx:XRP/USDT"
    ] = {
        "scanner_id": "htx:XRP/USDT",
        "healthy": False,
        "reason": "heartbeat_timeout",
    }

    supervisor = LiveFeedHealthSupervisor(
        scanner_health_monitor=scanner,
        connectivity_supervisor=connectivity,
    )

    result = supervisor.check_symbol(
        exchange_id="htx",
        symbol="XRP/USDT",
    )

    assert result["healthy"] is False
    assert result["reason"] == (
        "heartbeat_timeout"
    )


def test_normalizes_exchange_and_symbol():
    scanner = FakeScannerHealth()
    connectivity = FakeConnectivity()

    supervisor = LiveFeedHealthSupervisor(
        scanner_health_monitor=scanner,
        connectivity_supervisor=connectivity,
    )

    supervisor.record_success(
        exchange_id=" KUCOIN ",
        symbol=" btc/usdt ",
        latency_ms=10.0,
    )

    assert scanner.heartbeats[0][
        "scanner_id"
    ] == "kucoin:BTC/USDT"


def test_required_dependencies_are_validated():
    with pytest.raises(
        ValueError,
        match="scanner_health_monitor is required",
    ):
        LiveFeedHealthSupervisor(
            scanner_health_monitor=None,
            connectivity_supervisor=FakeConnectivity(),
        )

    with pytest.raises(
        ValueError,
        match="connectivity_supervisor is required",
    ):
        LiveFeedHealthSupervisor(
            scanner_health_monitor=FakeScannerHealth(),
            connectivity_supervisor=None,
        )


def test_supervisor_is_paper_safe():
    supervisor = LiveFeedHealthSupervisor(
        scanner_health_monitor=FakeScannerHealth(),
        connectivity_supervisor=FakeConnectivity(),
    )

    result = supervisor.record_success(
        exchange_id="bitget",
        symbol="SOL/USDT",
        latency_ms=15.0,
    )

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False
