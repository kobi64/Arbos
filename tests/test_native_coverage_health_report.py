import pytest

from core.native_coverage_health_report import (
    NativeCoverageHealthReport,
)


def make_result():
    return {
        "configured_exchange_count": 6,
        "enabled_exchange_ids": [
            "bitget",
            "digifinex",
            "gate",
            "htx",
            "kucoin",
            "xt",
        ],
        "exchange_count": 6,
        "successful_exchange_count": 6,
        "failed_exchange_count": 0,
        "orchestration_complete": True,
        "live_order_submitted": False,
        "audits": [
            {
                "exchange_id": "gate",
                "verified_raw_only_count": 0,
                "depth_sampled_count": 0,
                "usable_depth_count": 0,
                "usable_depth_ratio": 0.0,
                "fallback_coverage": "NOT_REQUIRED",
                "scan_failed": None,
            },
            {
                "exchange_id": "digifinex",
                "verified_raw_only_count": 513,
                "depth_sampled_count": 20,
                "usable_depth_count": 20,
                "usable_depth_ratio": 1.0,
                "fallback_coverage": "AVAILABLE",
                "scan_failed": None,
            },
        ],
        "priorities": [
            {
                "exchange_id": "digifinex",
                "implementation_status": "IMPLEMENTED",
                "verified_raw_only_count": 513,
                "usable_depth_ratio": 1.0,
            },
        ],
    }


def test_builds_healthy_report():
    reporter = NativeCoverageHealthReport()

    report = reporter.build(
        make_result()
    )

    assert report["status"] == "HEALTHY"
    assert report["healthy"] is True
    assert report["configured_exchange_count"] == 6
    assert report["successful_exchange_count"] == 6
    assert report["failed_exchange_count"] == 0


def test_aggregates_native_coverage_counts():
    reporter = NativeCoverageHealthReport()

    report = reporter.build(
        make_result()
    )

    assert report["verified_raw_only_count"] == 513
    assert report["depth_sampled_count"] == 20
    assert report["usable_depth_count"] == 20


def test_reports_available_fallback_exchanges():
    reporter = NativeCoverageHealthReport()

    report = reporter.build(
        make_result()
    )

    assert report[
        "fallback_available_exchange_ids"
    ] == [
        "digifinex",
    ]


def test_reports_failed_exchange_as_degraded():
    result = make_result()

    result["successful_exchange_count"] = 5
    result["failed_exchange_count"] = 1
    result["audits"].append({
        "exchange_id": "xt",
        "verified_raw_only_count": 0,
        "depth_sampled_count": 0,
        "usable_depth_count": 0,
        "usable_depth_ratio": 0.0,
        "fallback_coverage": "NOT_REQUIRED",
        "scan_failed": "NetworkError",
    })

    reporter = NativeCoverageHealthReport()

    report = reporter.build(result)

    assert report["status"] == "DEGRADED"
    assert report["healthy"] is False
    assert report["failed_exchange_ids"] == [
        "xt",
    ]


def test_incomplete_orchestration_is_degraded():
    result = make_result()
    result["orchestration_complete"] = False

    reporter = NativeCoverageHealthReport()

    report = reporter.build(result)

    assert report["status"] == "DEGRADED"
    assert report["healthy"] is False


def test_preserves_enabled_exchange_ids():
    reporter = NativeCoverageHealthReport()

    report = reporter.build(
        make_result()
    )

    assert report["enabled_exchange_ids"] == [
        "bitget",
        "digifinex",
        "gate",
        "htx",
        "kucoin",
        "xt",
    ]


def test_preserves_priority_summary():
    reporter = NativeCoverageHealthReport()

    report = reporter.build(
        make_result()
    )

    assert report["priorities"] == [
        {
            "exchange_id": "digifinex",
            "implementation_status": "IMPLEMENTED",
            "verified_raw_only_count": 513,
            "usable_depth_ratio": 1.0,
        },
    ]


def test_rejects_missing_result():
    reporter = NativeCoverageHealthReport()

    with pytest.raises(
        ValueError,
        match="coverage_result is required",
    ):
        reporter.build(None)


def test_report_is_observability_only():
    reporter = NativeCoverageHealthReport()

    report = reporter.build(
        make_result()
    )

    assert report[
        "live_order_submitted"
    ] is False
