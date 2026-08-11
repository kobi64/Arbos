import pytest

from core.native_coverage_health_regression_detector import (
    NativeCoverageHealthRegressionDetector,
)


def report(
    status="HEALTHY",
    healthy=True,
    verified=513,
    sampled=20,
    usable=20,
    fallback=None,
    failed=None,
):
    return {
        "status": status,
        "healthy": healthy,
        "configured_exchange_count": 6,
        "successful_exchange_count": (
            6 - len(failed or [])
        ),
        "failed_exchange_count": len(
            failed or []
        ),
        "verified_raw_only_count": verified,
        "depth_sampled_count": sampled,
        "usable_depth_count": usable,
        "fallback_available_exchange_ids": (
            list(
                fallback
                if fallback is not None
                else ["digifinex"]
            )
        ),
        "failed_exchange_ids": list(
            failed or []
        ),
        "report_complete": True,
        "live_order_submitted": False,
    }


def record(timestamp, health_report):
    return {
        "timestamp": float(timestamp),
        "report": health_report,
    }


def test_no_regression_when_health_is_unchanged():
    detector = (
        NativeCoverageHealthRegressionDetector()
    )

    result = detector.compare(
        previous=record(
            1000,
            report(),
        ),
        current=record(
            1060,
            report(),
        ),
    )

    assert result["regression_detected"] is False
    assert result["regression_count"] == 0
    assert result["regressions"] == []


def test_detects_healthy_to_degraded_transition():
    detector = (
        NativeCoverageHealthRegressionDetector()
    )

    result = detector.compare(
        previous=record(
            1000,
            report(),
        ),
        current=record(
            1060,
            report(
                status="DEGRADED",
                healthy=False,
                failed=["xt"],
            ),
        ),
    )

    types = [
        item["type"]
        for item in result["regressions"]
    ]

    assert "health_status_degraded" in types
    assert result["regression_detected"] is True


def test_detects_new_failed_exchange():
    detector = (
        NativeCoverageHealthRegressionDetector()
    )

    result = detector.compare(
        previous=record(
            1000,
            report(),
        ),
        current=record(
            1060,
            report(
                status="DEGRADED",
                healthy=False,
                failed=["xt"],
            ),
        ),
    )

    failures = [
        item
        for item in result["regressions"]
        if item["type"]
        == "new_failed_exchange"
    ]

    assert failures == [
        {
            "type": "new_failed_exchange",
            "exchange_id": "xt",
        },
    ]


def test_detects_loss_of_fallback_availability():
    detector = (
        NativeCoverageHealthRegressionDetector()
    )

    result = detector.compare(
        previous=record(
            1000,
            report(
                fallback=[
                    "digifinex",
                ]
            ),
        ),
        current=record(
            1060,
            report(
                fallback=[]
            ),
        ),
    )

    losses = [
        item
        for item in result["regressions"]
        if item["type"]
        == "fallback_availability_lost"
    ]

    assert losses == [
        {
            "type": (
                "fallback_availability_lost"
            ),
            "exchange_id": "digifinex",
        },
    ]


def test_detects_verified_coverage_decline():
    detector = (
        NativeCoverageHealthRegressionDetector()
    )

    result = detector.compare(
        previous=record(
            1000,
            report(
                verified=513
            ),
        ),
        current=record(
            1060,
            report(
                verified=500
            ),
        ),
    )

    decline = [
        item
        for item in result["regressions"]
        if item["type"]
        == "verified_raw_only_declined"
    ][0]

    assert decline["previous"] == 513
    assert decline["current"] == 500
    assert decline["delta"] == -13


def test_detects_usable_depth_decline():
    detector = (
        NativeCoverageHealthRegressionDetector()
    )

    result = detector.compare(
        previous=record(
            1000,
            report(
                sampled=20,
                usable=20,
            ),
        ),
        current=record(
            1060,
            report(
                sampled=20,
                usable=17,
            ),
        ),
    )

    decline = [
        item
        for item in result["regressions"]
        if item["type"]
        == "usable_depth_declined"
    ][0]

    assert decline["previous"] == 20
    assert decline["current"] == 17
    assert decline["delta"] == -3


def test_improvement_is_not_regression():
    detector = (
        NativeCoverageHealthRegressionDetector()
    )

    result = detector.compare(
        previous=record(
            1000,
            report(
                verified=500,
                usable=17,
            ),
        ),
        current=record(
            1060,
            report(
                verified=513,
                usable=20,
            ),
        ),
    )

    assert result["regression_detected"] is False
    assert result["regressions"] == []


def test_preserves_comparison_timestamps():
    detector = (
        NativeCoverageHealthRegressionDetector()
    )

    result = detector.compare(
        previous=record(
            1000,
            report(),
        ),
        current=record(
            1060,
            report(),
        ),
    )

    assert result[
        "previous_timestamp"
    ] == 1000.0

    assert result[
        "current_timestamp"
    ] == 1060.0


def test_requires_previous_record():
    detector = (
        NativeCoverageHealthRegressionDetector()
    )

    with pytest.raises(
        ValueError,
        match="previous record is required",
    ):
        detector.compare(
            previous=None,
            current=record(
                1060,
                report(),
            ),
        )


def test_requires_current_record():
    detector = (
        NativeCoverageHealthRegressionDetector()
    )

    with pytest.raises(
        ValueError,
        match="current record is required",
    ):
        detector.compare(
            previous=record(
                1000,
                report(),
            ),
            current=None,
        )


def test_detector_is_observability_only():
    detector = (
        NativeCoverageHealthRegressionDetector()
    )

    result = detector.compare(
        previous=record(
            1000,
            report(),
        ),
        current=record(
            1060,
            report(),
        ),
    )

    assert result[
        "live_order_submitted"
    ] is False
