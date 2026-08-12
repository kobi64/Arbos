"""
ArbOS™
EX-207
Live Feed Health Supervisor

Combines per-symbol feed heartbeat health with
exchange-level connectivity health.

Reuses existing ArbOS™ health primitives.

Paper/public-data infrastructure only.
No authentication.
No transfers.
No live orders.
"""


class LiveFeedHealthSupervisor:
    def __init__(
        self,
        scanner_health_monitor,
        connectivity_supervisor,
    ):
        if scanner_health_monitor is None:
            raise ValueError(
                "scanner_health_monitor is required"
            )

        if connectivity_supervisor is None:
            raise ValueError(
                "connectivity_supervisor is required"
            )

        self._scanner_health_monitor = (
            scanner_health_monitor
        )
        self._connectivity_supervisor = (
            connectivity_supervisor
        )

    def record_success(
        self,
        exchange_id,
        symbol,
        latency_ms,
    ):
        exchange_id, symbol = (
            self._normalize(
                exchange_id,
                symbol,
            )
        )

        scanner_id = (
            f"{exchange_id}:{symbol}"
        )

        scanner_result = (
            self._scanner_health_monitor
            .record_heartbeat(
                scanner_id=scanner_id,
                latency_ms=latency_ms,
                opportunities_found=0,
            )
        )

        connectivity_result = (
            self._connectivity_supervisor
            .record_heartbeat(
                exchange_id=exchange_id,
                latency_ms=latency_ms,
                connected=True,
            )
        )

        healthy = (
            scanner_result.get(
                "healthy"
            )
            is True
            and connectivity_result.get(
                "healthy"
            )
            is True
        )

        reason = None

        if not healthy:
            reason = (
                scanner_result.get(
                    "reason"
                )
                or connectivity_result.get(
                    "reason"
                )
            )

        return {
            "exchange_id": exchange_id,
            "symbol": symbol,
            "scanner_id": scanner_id,
            "healthy": healthy,
            "reason": reason,
            "paper_only": True,
            "live_order_submitted": False,
        }

    def record_failure(
        self,
        exchange_id,
        symbol,
        latency_ms,
        reason,
    ):
        exchange_id, symbol = (
            self._normalize(
                exchange_id,
                symbol,
            )
        )

        scanner_id = (
            f"{exchange_id}:{symbol}"
        )

        self._connectivity_supervisor.record_heartbeat(
            exchange_id=exchange_id,
            latency_ms=latency_ms,
            connected=False,
        )

        return {
            "exchange_id": exchange_id,
            "symbol": symbol,
            "scanner_id": scanner_id,
            "healthy": False,
            "reason": str(
                reason
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def check_symbol(
        self,
        exchange_id,
        symbol,
    ):
        exchange_id, symbol = (
            self._normalize(
                exchange_id,
                symbol,
            )
        )

        scanner_id = (
            f"{exchange_id}:{symbol}"
        )

        scanner_result = (
            self._scanner_health_monitor
            .check_health(
                scanner_id
            )
        )

        connectivity_result = (
            self._connectivity_supervisor
            .check_health(
                exchange_id
            )
        )

        if (
            scanner_result.get(
                "healthy"
            )
            is not True
        ):
            return {
                "exchange_id": exchange_id,
                "symbol": symbol,
                "healthy": False,
                "reason": (
                    scanner_result.get(
                        "reason"
                    )
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        if (
            connectivity_result.get(
                "healthy"
            )
            is not True
        ):
            return {
                "exchange_id": exchange_id,
                "symbol": symbol,
                "healthy": False,
                "reason": (
                    connectivity_result.get(
                        "reason"
                    )
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        return {
            "exchange_id": exchange_id,
            "symbol": symbol,
            "healthy": True,
            "reason": None,
            "paper_only": True,
            "live_order_submitted": False,
        }

    @staticmethod
    def _normalize(
        exchange_id,
        symbol,
    ):
        exchange_id = str(
            exchange_id
            or ""
        ).strip().lower()

        symbol = str(
            symbol
            or ""
        ).strip().upper()

        if not exchange_id:
            raise ValueError(
                "exchange_id is required"
            )

        if not symbol:
            raise ValueError(
                "symbol is required"
            )

        return (
            exchange_id,
            symbol,
        )
