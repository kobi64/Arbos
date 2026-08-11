import pytest

from core.scanner_preflight_readiness_gate import (
    ScannerPreflightReadinessGate,
)


def healthy_report():
    return {
        "status": "HEALTHY",
        "healthy": True,
        "failed_exchange_count": 0,
        "live_order_submitted": False,
    }


def no_alerts():
    return {
        "alert_required": False,
        "highest_severity": "NONE",
        "alert_count": 0,
        "live_order_submitted": False,
    }


def ready_session():
    return {
        "session_ready": True,
        "reason": "live_market_paper_session_ready",
        "mode": "PAPER",
        "paper_only": True,
        "live_execution_enabled": False,
        "live_order_submitted": False,
    }


def test_ready_preflight_allows_scanner_start():
    result = ScannerPreflightReadinessGate().evaluate(
        health_report=healthy_report(),
        alert_summary=no_alerts(),
        session_readiness=ready_session(),
    )

    assert result["scanner_ready"] is True
    assert result["reason"] == "scanner_preflight_ready"
    assert result["mode"] == "PAPER"


def test_degraded_health_blocks_scanner():
    health = healthy_report()
    health["healthy"] = False
    health["status"] = "DEGRADED"

    result = ScannerPreflightReadinessGate().evaluate(
        health_report=health,
        alert_summary=no_alerts(),
        session_readiness=ready_session(),
    )

    assert result["scanner_ready"] is False
    assert result["reason"] == "coverage_health_degraded"


def test_critical_alert_blocks_scanner():
    alerts = {
        "alert_required": True,
        "highest_severity": "CRITICAL",
        "alert_count": 1,
        "live_order_submitted": False,
    }

    result = ScannerPreflightReadinessGate().evaluate(
        health_report=healthy_report(),
        alert_summary=alerts,
        session_readiness=ready_session(),
    )

    assert result["scanner_ready"] is False
    assert result["reason"] == "critical_coverage_regression"


def test_warning_alert_does_not_block_scanner():
    alerts = {
        "alert_required": True,
        "highest_severity": "WARNING",
        "alert_count": 1,
        "live_order_submitted": False,
    }

    result = ScannerPreflightReadinessGate().evaluate(
        health_report=healthy_report(),
        alert_summary=alerts,
        session_readiness=ready_session(),
    )

    assert result["scanner_ready"] is True


def test_unready_paper_session_blocks_scanner():
    session = ready_session()
    session["session_ready"] = False
    session["reason"] = "stale_market_data"

    result = ScannerPreflightReadinessGate().evaluate(
        health_report=healthy_report(),
        alert_summary=no_alerts(),
        session_readiness=session,
    )

    assert result["scanner_ready"] is False
    assert result["reason"] == "paper_session_not_ready"


def test_non_paper_session_is_blocked():
    session = ready_session()
    session["paper_only"] = False

    result = ScannerPreflightReadinessGate().evaluate(
        health_report=healthy_report(),
        alert_summary=no_alerts(),
        session_readiness=session,
    )

    assert result["scanner_ready"] is False
    assert result["reason"] == "paper_only_required"


def test_previous_live_submission_blocks_scanner():
    health = healthy_report()
    health["live_order_submitted"] = True

    result = ScannerPreflightReadinessGate().evaluate(
        health_report=health,
        alert_summary=no_alerts(),
        session_readiness=ready_session(),
    )

    assert result["scanner_ready"] is False
    assert result["reason"] == "live_order_already_submitted"


def test_requires_health_report():
    with pytest.raises(
        ValueError,
        match="health_report is required",
    ):
        ScannerPreflightReadinessGate().evaluate(
            health_report=None,
            alert_summary=no_alerts(),
            session_readiness=ready_session(),
        )


def test_requires_alert_summary():
    with pytest.raises(
        ValueError,
        match="alert_summary is required",
    ):
        ScannerPreflightReadinessGate().evaluate(
            health_report=healthy_report(),
            alert_summary=None,
            session_readiness=ready_session(),
        )


def test_requires_session_readiness():
    with pytest.raises(
        ValueError,
        match="session_readiness is required",
    ):
        ScannerPreflightReadinessGate().evaluate(
            health_report=healthy_report(),
            alert_summary=no_alerts(),
            session_readiness=None,
        )


def test_preflight_is_explicitly_non_live():
    result = ScannerPreflightReadinessGate().evaluate(
        health_report=healthy_report(),
        alert_summary=no_alerts(),
        session_readiness=ready_session(),
    )

    assert result["paper_only"] is True
    assert result["live_execution_enabled"] is False
    assert result["live_order_submitted"] is False
