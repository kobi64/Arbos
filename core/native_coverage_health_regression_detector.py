"""
ArbOS™
EX-194
Native Coverage Health Regression Detector

Compares consecutive native coverage health history records
and reports deterioration only.

Observability only.
No authentication.
No transfers.
No live orders.
"""


class NativeCoverageHealthRegressionDetector:
    def compare(
        self,
        previous,
        current,
    ):
        if previous is None:
            raise ValueError(
                "previous record is required"
            )

        if current is None:
            raise ValueError(
                "current record is required"
            )

        previous_report = (
            previous.get("report", {})
            if isinstance(previous, dict)
            else {}
        )

        current_report = (
            current.get("report", {})
            if isinstance(current, dict)
            else {}
        )

        regressions = []

        previous_healthy = bool(
            previous_report.get(
                "healthy",
                False,
            )
        )

        current_healthy = bool(
            current_report.get(
                "healthy",
                False,
            )
        )

        if (
            previous_healthy
            and not current_healthy
        ):
            regressions.append({
                "type": (
                    "health_status_degraded"
                ),
                "previous_status": (
                    previous_report.get(
                        "status"
                    )
                ),
                "current_status": (
                    current_report.get(
                        "status"
                    )
                ),
            })

        previous_failed = set(
            previous_report.get(
                "failed_exchange_ids",
                [],
            )
            or []
        )

        current_failed = set(
            current_report.get(
                "failed_exchange_ids",
                [],
            )
            or []
        )

        for exchange_id in sorted(
            current_failed - previous_failed
        ):
            regressions.append({
                "type": (
                    "new_failed_exchange"
                ),
                "exchange_id": (
                    exchange_id
                ),
            })

        previous_fallback = set(
            previous_report.get(
                "fallback_available_exchange_ids",
                [],
            )
            or []
        )

        current_fallback = set(
            current_report.get(
                "fallback_available_exchange_ids",
                [],
            )
            or []
        )

        for exchange_id in sorted(
            previous_fallback
            - current_fallback
        ):
            regressions.append({
                "type": (
                    "fallback_availability_lost"
                ),
                "exchange_id": (
                    exchange_id
                ),
            })

        previous_verified = int(
            previous_report.get(
                "verified_raw_only_count",
                0,
            )
            or 0
        )

        current_verified = int(
            current_report.get(
                "verified_raw_only_count",
                0,
            )
            or 0
        )

        if current_verified < previous_verified:
            regressions.append({
                "type": (
                    "verified_raw_only_declined"
                ),
                "previous": (
                    previous_verified
                ),
                "current": (
                    current_verified
                ),
                "delta": (
                    current_verified
                    - previous_verified
                ),
            })

        previous_usable = int(
            previous_report.get(
                "usable_depth_count",
                0,
            )
            or 0
        )

        current_usable = int(
            current_report.get(
                "usable_depth_count",
                0,
            )
            or 0
        )

        if current_usable < previous_usable:
            regressions.append({
                "type": (
                    "usable_depth_declined"
                ),
                "previous": (
                    previous_usable
                ),
                "current": (
                    current_usable
                ),
                "delta": (
                    current_usable
                    - previous_usable
                ),
            })

        return {
            "previous_timestamp": float(
                previous.get(
                    "timestamp",
                    0.0,
                )
                or 0.0
            ),
            "current_timestamp": float(
                current.get(
                    "timestamp",
                    0.0,
                )
                or 0.0
            ),
            "regression_detected": bool(
                regressions
            ),
            "regression_count": len(
                regressions
            ),
            "regressions": regressions,
            "comparison_complete": True,
            "live_order_submitted": False,
        }
