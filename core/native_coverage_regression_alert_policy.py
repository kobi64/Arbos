"""
ArbOS™
EX-195
Native Coverage Regression Alert Policy

Classifies EX-194 native coverage regressions by severity
and determines whether an alert is required.

Observability only.
No authentication.
No transfers.
No live orders.
"""


class NativeCoverageRegressionAlertPolicy:
    _CRITICAL_TYPES = {
        "health_status_degraded",
        "new_failed_exchange",
        "fallback_availability_lost",
    }

    _WARNING_TYPES = {
        "usable_depth_declined",
        "verified_raw_only_declined",
    }

    def evaluate(
        self,
        regression,
    ):
        if regression is None:
            raise ValueError(
                "regression is required"
            )

        regression_type = str(
            regression.get(
                "type",
                "",
            )
            or ""
        ).strip()

        if regression_type in self._CRITICAL_TYPES:
            severity = "CRITICAL"
            alert = True
        elif regression_type in self._WARNING_TYPES:
            severity = "WARNING"
            alert = True
        else:
            severity = "INFO"
            alert = False

        return {
            "severity": severity,
            "alert": alert,
            "regression": dict(
                regression
            ),
            "live_order_submitted": False,
        }
