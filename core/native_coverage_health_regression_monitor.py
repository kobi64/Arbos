"""
ArbOS™
EX-194
Native Coverage Health Regression Monitor

Reads the two most recent persisted native coverage health records
and delegates regression comparison to the EX-194 detector.

Observability only.
No authentication.
No transfers.
No live orders.
"""


class NativeCoverageHealthRegressionMonitor:
    def __init__(
        self,
        history_store,
        detector,
    ):
        if history_store is None:
            raise ValueError(
                "history_store is required"
            )

        if detector is None:
            raise ValueError(
                "detector is required"
            )

        self._history_store = history_store
        self._detector = detector

    def check(self):
        records = self._history_store.history(
            limit=2
        )

        record_count = len(records)

        if record_count < 2:
            return {
                "regression_detected": False,
                "regression_count": 0,
                "regressions": [],
                "comparison_complete": False,
                "reason": "insufficient_history",
                "history_record_count": record_count,
                "live_order_submitted": False,
            }

        result = self._detector.compare(
            previous=records[-2],
            current=records[-1],
        )

        return {
            **result,
            "history_record_count": 2,
            "live_order_submitted": False,
        }
