"""
ArbOS™
EX-175
Live Market Paper Session Readiness

Final session-level readiness boundary before an ArbOS paper
trading session using real public market data.

This module is deliberately paper-only.

It does not submit, authorize, prepare, or permit live exchange
orders. A session can become ready only when all required
paper-trading safety conditions are satisfied.
"""


class LiveMarketPaperSessionReadiness:
    def __init__(self):
        self._history = []

    def evaluate(
        self,
        verification_result,
        exchange_connected,
        market_data_available,
        market_data_fresh,
        paper_engine_ready,
        risk_controls_ready,
        audit_ready,
        session_enabled=True,
    ):
        if verification_result is None:
            raise ValueError(
                "verification_result is required"
            )

        boolean_inputs = {
            "exchange_connected": exchange_connected,
            "market_data_available": market_data_available,
            "market_data_fresh": market_data_fresh,
            "paper_engine_ready": paper_engine_ready,
            "risk_controls_ready": risk_controls_ready,
            "audit_ready": audit_ready,
            "session_enabled": session_enabled,
        }

        for name, value in boolean_inputs.items():
            if not isinstance(value, bool):
                raise ValueError(
                    f"{name} must be boolean"
                )

        if verification_result.get(
            "live_order_submitted"
        ) is True:
            return self._blocked(
                "live_order_already_submitted"
            )

        if verification_result.get(
            "paper_only"
        ) is not True:
            return self._blocked(
                "paper_verification_required"
            )

        if not session_enabled:
            return self._blocked(
                "paper_session_disabled"
            )

        if not exchange_connected:
            return self._blocked(
                "exchange_not_connected"
            )

        if not market_data_available:
            return self._blocked(
                "market_data_unavailable"
            )

        if not market_data_fresh:
            return self._blocked(
                "stale_market_data"
            )

        if not paper_engine_ready:
            return self._blocked(
                "paper_engine_not_ready"
            )

        if not risk_controls_ready:
            return self._blocked(
                "risk_controls_not_ready"
            )

        if not audit_ready:
            return self._blocked(
                "audit_not_ready"
            )

        result = {
            "session_ready": True,
            "reason": (
                "live_market_paper_session_ready"
            ),
            "mode": "PAPER",
            "real_market_data": True,
            "simulated_execution": True,
            "paper_only": True,
            "live_execution_enabled": False,
            "live_order_submitted": False,
        }

        return self._record(result)

    def history(self):
        return [
            dict(record)
            for record in self._history
        ]

    def _blocked(self, reason):
        return self._record({
            "session_ready": False,
            "reason": reason,
            "mode": "PAPER",
            "real_market_data": True,
            "simulated_execution": True,
            "paper_only": True,
            "live_execution_enabled": False,
            "live_order_submitted": False,
        })

    def _record(self, result):
        self._history.append(
            dict(result)
        )
        return dict(result)
