"""
ArbOS™
EX-195
Native Coverage Regression Alert Coordinator

Aggregates EX-194 regression alert-policy decisions into a single
alert summary.

Observability only.
No authentication.
No transfers.
No live orders.
"""


class NativeCoverageRegressionAlertCoordinator:
    _SEVERITY_RANK = {
        "NONE": 0,
        "INFO": 1,
        "WARNING": 2,
        "CRITICAL": 3,
    }

    def __init__(
        self,
        policy,
    ):
        if policy is None:
            raise ValueError(
                "policy is required"
            )

        self._policy = policy

    def evaluate(
        self,
        regression_result,
    ):
        if regression_result is None:
            raise ValueError(
                "regression_result is required"
            )

        regressions = regression_result.get(
            "regressions",
            [],
        )

        decisions = []

        for regression in regressions:
            if not isinstance(
                regression,
                dict,
            ):
                continue

            decisions.append(
                self._policy.evaluate(
                    regression
                )
            )

        alert_decisions = [
            decision
            for decision in decisions
            if decision.get("alert") is True
        ]

        highest_severity = "NONE"

        for decision in decisions:
            severity = str(
                decision.get(
                    "severity",
                    "INFO",
                )
                or "INFO"
            ).strip().upper()

            if (
                self._SEVERITY_RANK.get(
                    severity,
                    0,
                )
                > self._SEVERITY_RANK[
                    highest_severity
                ]
            ):
                highest_severity = severity

        return {
            "alert_required": bool(
                alert_decisions
            ),
            "highest_severity": (
                highest_severity
            ),
            "alert_count": len(
                alert_decisions
            ),
            "decision_count": len(
                decisions
            ),
            "decisions": decisions,
            "evaluation_complete": True,
            "live_order_submitted": False,
        }
