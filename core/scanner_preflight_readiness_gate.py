"""
ArbOS™
EX-196
Scanner Pre-Flight Readiness Gate

Final safety decision before starting a live-market,
paper-only scanner session.

Consumes:
- native coverage health
- native coverage regression alert summary
- live market paper session readiness

Decision only.
No authentication.
No transfers.
No live orders.
"""


class ScannerPreflightReadinessGate:
    def evaluate(
        self,
        health_report,
        alert_summary,
        session_readiness,
    ):
        if health_report is None:
            raise ValueError(
                "health_report is required"
            )

        if alert_summary is None:
            raise ValueError(
                "alert_summary is required"
            )

        if session_readiness is None:
            raise ValueError(
                "session_readiness is required"
            )

        if (
            health_report.get(
                "live_order_submitted"
            ) is True
            or alert_summary.get(
                "live_order_submitted"
            ) is True
            or session_readiness.get(
                "live_order_submitted"
            ) is True
        ):
            return self._blocked(
                "live_order_already_submitted"
            )

        if (
            session_readiness.get(
                "paper_only"
            ) is not True
            or session_readiness.get(
                "live_execution_enabled"
            ) is True
        ):
            return self._blocked(
                "paper_only_required"
            )

        if (
            health_report.get(
                "healthy"
            ) is not True
        ):
            return self._blocked(
                "coverage_health_degraded"
            )

        highest_severity = str(
            alert_summary.get(
                "highest_severity",
                "NONE",
            )
            or "NONE"
        ).strip().upper()

        if (
            alert_summary.get(
                "alert_required"
            ) is True
            and highest_severity
            == "CRITICAL"
        ):
            return self._blocked(
                "critical_coverage_regression"
            )

        if (
            session_readiness.get(
                "session_ready"
            ) is not True
        ):
            return self._blocked(
                "paper_session_not_ready"
            )

        return {
            "scanner_ready": True,
            "reason": "scanner_preflight_ready",
            "mode": "PAPER",
            "paper_only": True,
            "live_execution_enabled": False,
            "live_order_submitted": False,
        }

    @staticmethod
    def _blocked(reason):
        return {
            "scanner_ready": False,
            "reason": reason,
            "mode": "PAPER",
            "paper_only": True,
            "live_execution_enabled": False,
            "live_order_submitted": False,
        }
