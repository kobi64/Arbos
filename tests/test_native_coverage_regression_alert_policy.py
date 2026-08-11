import pytest

from core.native_coverage_regression_alert_policy import (
    NativeCoverageRegressionAlertPolicy,
)


def test_health_status_degraded_is_critical_alert():
    result = NativeCoverageRegressionAlertPolicy().evaluate({
        "type": "health_status_degraded",
    })

    assert result["severity"] == "CRITICAL"
    assert result["alert"] is True


def test_new_failed_exchange_is_critical_alert():
    result = NativeCoverageRegressionAlertPolicy().evaluate({
        "type": "new_failed_exchange",
        "exchange_id": "xt",
    })

    assert result["severity"] == "CRITICAL"
    assert result["alert"] is True


def test_fallback_loss_is_critical_alert():
    result = NativeCoverageRegressionAlertPolicy().evaluate({
        "type": "fallback_availability_lost",
        "exchange_id": "digifinex",
    })

    assert result["severity"] == "CRITICAL"
    assert result["alert"] is True


def test_usable_depth_decline_is_warning_alert():
    result = NativeCoverageRegressionAlertPolicy().evaluate({
        "type": "usable_depth_declined",
        "previous": 20,
        "current": 17,
    })

    assert result["severity"] == "WARNING"
    assert result["alert"] is True


def test_verified_coverage_decline_is_warning_alert():
    result = NativeCoverageRegressionAlertPolicy().evaluate({
        "type": "verified_raw_only_declined",
        "previous": 513,
        "current": 500,
    })

    assert result["severity"] == "WARNING"
    assert result["alert"] is True


def test_unknown_regression_is_info_log_only():
    result = NativeCoverageRegressionAlertPolicy().evaluate({
        "type": "unknown_regression",
    })

    assert result["severity"] == "INFO"
    assert result["alert"] is False


def test_preserves_regression_payload():
    regression = {
        "type": "new_failed_exchange",
        "exchange_id": "xt",
    }

    result = NativeCoverageRegressionAlertPolicy().evaluate(
        regression
    )

    assert result["regression"] == regression


def test_requires_regression():
    with pytest.raises(
        ValueError,
        match="regression is required",
    ):
        NativeCoverageRegressionAlertPolicy().evaluate(
            None
        )


def test_policy_is_observability_only():
    result = NativeCoverageRegressionAlertPolicy().evaluate({
        "type": "usable_depth_declined",
    })

    assert result["live_order_submitted"] is False
