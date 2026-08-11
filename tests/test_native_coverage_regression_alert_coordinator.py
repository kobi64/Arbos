import pytest

from core.native_coverage_regression_alert_coordinator import (
    NativeCoverageRegressionAlertCoordinator,
)


class FakePolicy:
    def evaluate(self, regression):
        regression_type = regression.get("type")

        if regression_type == "new_failed_exchange":
            return {
                "severity": "CRITICAL",
                "alert": True,
                "regression": regression,
                "live_order_submitted": False,
            }

        if regression_type == "usable_depth_declined":
            return {
                "severity": "WARNING",
                "alert": True,
                "regression": regression,
                "live_order_submitted": False,
            }

        return {
            "severity": "INFO",
            "alert": False,
            "regression": regression,
            "live_order_submitted": False,
        }


def test_aggregates_regression_alert_decisions():
    result = (
        NativeCoverageRegressionAlertCoordinator(
            policy=FakePolicy(),
        ).evaluate({
            "regression_detected": True,
            "regressions": [
                {
                    "type": "new_failed_exchange",
                    "exchange_id": "xt",
                },
                {
                    "type": "usable_depth_declined",
                    "previous": 20,
                    "current": 17,
                },
            ],
        })
    )

    assert result["alert_required"] is True
    assert result["highest_severity"] == "CRITICAL"
    assert result["alert_count"] == 2
    assert len(result["decisions"]) == 2


def test_warning_is_highest_when_no_critical():
    result = (
        NativeCoverageRegressionAlertCoordinator(
            policy=FakePolicy(),
        ).evaluate({
            "regression_detected": True,
            "regressions": [
                {
                    "type": "usable_depth_declined",
                },
            ],
        })
    )

    assert result["highest_severity"] == "WARNING"
    assert result["alert_required"] is True


def test_info_only_result_does_not_alert():
    result = (
        NativeCoverageRegressionAlertCoordinator(
            policy=FakePolicy(),
        ).evaluate({
            "regression_detected": True,
            "regressions": [
                {
                    "type": "unknown_regression",
                },
            ],
        })
    )

    assert result["highest_severity"] == "INFO"
    assert result["alert_required"] is False
    assert result["alert_count"] == 0


def test_no_regressions_produces_no_alert():
    result = (
        NativeCoverageRegressionAlertCoordinator(
            policy=FakePolicy(),
        ).evaluate({
            "regression_detected": False,
            "regressions": [],
        })
    )

    assert result["alert_required"] is False
    assert result["highest_severity"] == "NONE"
    assert result["alert_count"] == 0
    assert result["decisions"] == []


def test_requires_regression_result():
    with pytest.raises(
        ValueError,
        match="regression_result is required",
    ):
        NativeCoverageRegressionAlertCoordinator(
            policy=FakePolicy(),
        ).evaluate(None)


def test_requires_policy():
    with pytest.raises(
        ValueError,
        match="policy is required",
    ):
        NativeCoverageRegressionAlertCoordinator(
            policy=None,
        )


def test_coordinator_is_observability_only():
    result = (
        NativeCoverageRegressionAlertCoordinator(
            policy=FakePolicy(),
        ).evaluate({
            "regression_detected": False,
            "regressions": [],
        })
    )

    assert result["live_order_submitted"] is False
