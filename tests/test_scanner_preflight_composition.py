from core.live_market_paper_session_readiness import (
    LiveMarketPaperSessionReadiness,
)
from core.scanner_preflight_readiness_gate import (
    ScannerPreflightReadinessGate,
)


def test_real_paper_readiness_contract_passes_preflight():
    session = LiveMarketPaperSessionReadiness().evaluate(
        verification_result={
            "paper_only": True,
            "live_order_submitted": False,
        },
        exchange_connected=True,
        market_data_available=True,
        market_data_fresh=True,
        paper_engine_ready=True,
        risk_controls_ready=True,
        audit_ready=True,
        session_enabled=True,
    )

    result = ScannerPreflightReadinessGate().evaluate(
        health_report={
            "status": "HEALTHY",
            "healthy": True,
            "live_order_submitted": False,
        },
        alert_summary={
            "alert_required": False,
            "highest_severity": "NONE",
            "alert_count": 0,
            "live_order_submitted": False,
        },
        session_readiness=session,
    )

    assert result["scanner_ready"] is True
    assert result["reason"] == "scanner_preflight_ready"
    assert result["paper_only"] is True
    assert result["live_execution_enabled"] is False
    assert result["live_order_submitted"] is False


def test_critical_regression_blocks_ready_paper_session():
    session = LiveMarketPaperSessionReadiness().evaluate(
        verification_result={
            "paper_only": True,
            "live_order_submitted": False,
        },
        exchange_connected=True,
        market_data_available=True,
        market_data_fresh=True,
        paper_engine_ready=True,
        risk_controls_ready=True,
        audit_ready=True,
        session_enabled=True,
    )

    result = ScannerPreflightReadinessGate().evaluate(
        health_report={
            "status": "HEALTHY",
            "healthy": True,
            "live_order_submitted": False,
        },
        alert_summary={
            "alert_required": True,
            "highest_severity": "CRITICAL",
            "alert_count": 1,
            "live_order_submitted": False,
        },
        session_readiness=session,
    )

    assert result["scanner_ready"] is False
    assert result["reason"] == "critical_coverage_regression"
