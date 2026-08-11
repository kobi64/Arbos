import pytest

from core.native_coverage_health_regression_monitor import (
    NativeCoverageHealthRegressionMonitor,
)


class FakeHistoryStore:
    def __init__(self, records):
        self.records = records
        self.limit = None

    def history(self, limit=None):
        self.limit = limit

        if limit is None:
            return list(self.records)

        return list(
            self.records[-limit:]
        )


class FakeDetector:
    def __init__(self):
        self.previous = None
        self.current = None

    def compare(
        self,
        previous,
        current,
    ):
        self.previous = previous
        self.current = current

        return {
            "regression_detected": False,
            "regression_count": 0,
            "regressions": [],
            "comparison_complete": True,
            "live_order_submitted": False,
        }


def record(timestamp, status="HEALTHY"):
    return {
        "timestamp": float(timestamp),
        "report": {
            "status": status,
            "healthy": status == "HEALTHY",
            "live_order_submitted": False,
        },
    }


def test_compares_latest_two_history_records():
    store = FakeHistoryStore([
        record(1000),
        record(1060),
        record(1120),
    ])

    detector = FakeDetector()

    monitor = (
        NativeCoverageHealthRegressionMonitor(
            history_store=store,
            detector=detector,
        )
    )

    result = monitor.check()

    assert store.limit == 2

    assert detector.previous[
        "timestamp"
    ] == 1060.0

    assert detector.current[
        "timestamp"
    ] == 1120.0

    assert result[
        "comparison_complete"
    ] is True


def test_reports_insufficient_history_when_empty():
    monitor = (
        NativeCoverageHealthRegressionMonitor(
            history_store=FakeHistoryStore([]),
            detector=FakeDetector(),
        )
    )

    result = monitor.check()

    assert result[
        "comparison_complete"
    ] is False

    assert result[
        "reason"
    ] == "insufficient_history"

    assert result[
        "history_record_count"
    ] == 0


def test_reports_insufficient_history_with_one_record():
    monitor = (
        NativeCoverageHealthRegressionMonitor(
            history_store=FakeHistoryStore([
                record(1000),
            ]),
            detector=FakeDetector(),
        )
    )

    result = monitor.check()

    assert result[
        "comparison_complete"
    ] is False

    assert result[
        "reason"
    ] == "insufficient_history"

    assert result[
        "history_record_count"
    ] == 1


def test_preserves_detector_regression_result():
    class RegressionDetector:
        def compare(
            self,
            previous,
            current,
        ):
            return {
                "regression_detected": True,
                "regression_count": 1,
                "regressions": [
                    {
                        "type": (
                            "usable_depth_declined"
                        ),
                        "previous": 20,
                        "current": 17,
                        "delta": -3,
                    },
                ],
                "comparison_complete": True,
                "live_order_submitted": False,
            }

    monitor = (
        NativeCoverageHealthRegressionMonitor(
            history_store=FakeHistoryStore([
                record(1000),
                record(1060),
            ]),
            detector=RegressionDetector(),
        )
    )

    result = monitor.check()

    assert result[
        "regression_detected"
    ] is True

    assert result[
        "regression_count"
    ] == 1

    assert result["regressions"][0][
        "type"
    ] == "usable_depth_declined"


def test_requires_history_store():
    with pytest.raises(
        ValueError,
        match="history_store is required",
    ):
        NativeCoverageHealthRegressionMonitor(
            history_store=None,
            detector=FakeDetector(),
        )


def test_requires_detector():
    with pytest.raises(
        ValueError,
        match="detector is required",
    ):
        NativeCoverageHealthRegressionMonitor(
            history_store=FakeHistoryStore([]),
            detector=None,
        )


def test_monitor_is_observability_only():
    monitor = (
        NativeCoverageHealthRegressionMonitor(
            history_store=FakeHistoryStore([]),
            detector=FakeDetector(),
        )
    )

    result = monitor.check()

    assert result[
        "live_order_submitted"
    ] is False
