from exchanges.native_coverage_prioritizer import (
    NativeCoveragePrioritizer,
)


def test_prioritizes_large_verified_usable_coverage():
    audits = [
        {
            "exchange_id": "digifinex",
            "verified_raw_only_count": 513,
            "depth_sampled_count": 20,
            "usable_depth_count": 20,
            "usable_depth_ratio": 1.0,
            "fallback_coverage": "AVAILABLE",
        },
        {
            "exchange_id": "kucoin",
            "verified_raw_only_count": 0,
            "depth_sampled_count": 0,
            "usable_depth_count": 0,
            "usable_depth_ratio": 0.0,
            "fallback_coverage": "NOT_REQUIRED",
        },
    ]

    result = NativeCoveragePrioritizer().prioritize(
        audits
    )

    assert result["priorities"][0][
        "exchange_id"
    ] == "digifinex"

    assert result["priorities"][0][
        "verified_raw_only_count"
    ] == 513

    assert result["priorities"][0][
        "usable_depth_ratio"
    ] == 1.0


def test_measured_depth_breaks_equal_coverage_tie():
    audits = [
        {
            "exchange_id": "alpha",
            "verified_raw_only_count": 100,
            "depth_sampled_count": 10,
            "usable_depth_count": 5,
            "usable_depth_ratio": 0.5,
            "fallback_coverage": "AVAILABLE",
        },
        {
            "exchange_id": "beta",
            "verified_raw_only_count": 100,
            "depth_sampled_count": 10,
            "usable_depth_count": 10,
            "usable_depth_ratio": 1.0,
            "fallback_coverage": "AVAILABLE",
        },
    ]

    result = NativeCoveragePrioritizer().prioritize(
        audits
    )

    assert [
        item["exchange_id"]
        for item in result["priorities"]
    ] == [
        "beta",
        "alpha",
    ]


def test_does_not_extrapolate_sample_to_all_markets():
    audits = [
        {
            "exchange_id": "digifinex",
            "verified_raw_only_count": 513,
            "depth_sampled_count": 20,
            "usable_depth_count": 20,
            "usable_depth_ratio": 1.0,
            "fallback_coverage": "AVAILABLE",
        },
    ]

    result = NativeCoveragePrioritizer().prioritize(
        audits
    )

    priority = result["priorities"][0]

    assert (
        "estimated_usable_market_count"
        not in priority
    )

    assert priority[
        "verified_raw_only_count"
    ] == 513

    assert priority[
        "usable_depth_count"
    ] == 20


def test_failed_exchange_is_not_ranked():
    audits = [
        {
            "exchange_id": "broken",
            "scan_failed": True,
            "verified_raw_only_count": 999,
        },
        {
            "exchange_id": "healthy",
            "scan_failed": False,
            "verified_raw_only_count": 10,
            "depth_sampled_count": 5,
            "usable_depth_count": 5,
            "usable_depth_ratio": 1.0,
            "fallback_coverage": "AVAILABLE",
        },
    ]

    result = NativeCoveragePrioritizer().prioritize(
        audits
    )

    assert len(result["priorities"]) == 1
    assert result["priorities"][0][
        "exchange_id"
    ] == "healthy"

    assert result["excluded_exchange_count"] == 1


def test_not_required_exchange_has_no_implementation_need():
    audits = [
        {
            "exchange_id": "kucoin",
            "verified_raw_only_count": 0,
            "depth_sampled_count": 0,
            "usable_depth_count": 0,
            "usable_depth_ratio": 0.0,
            "fallback_coverage": "NOT_REQUIRED",
        },
    ]

    result = NativeCoveragePrioritizer().prioritize(
        audits
    )

    priority = result["priorities"][0]

    assert priority[
        "implementation_required"
    ] is False

    assert priority[
        "priority_reason"
    ] == "native_fallback_not_required"


def test_requires_audits():
    try:
        NativeCoveragePrioritizer().prioritize(
            None
        )
        assert False
    except ValueError as exc:
        assert str(exc) == "audits are required"


def test_prioritizer_is_research_only():
    result = NativeCoveragePrioritizer().prioritize(
        []
    )

    assert result["priority_complete"] is True
    assert result["live_order_submitted"] is False


def test_prioritizes_real_ex186_result_shape():
    scan_result = {
        "audits": [
            {
                "exchange_id": "digifinex",
                "scan_failed": False,
                "verified_raw_only_count": 513,
                "depth_sampled_count": 20,
                "usable_depth_count": 20,
                "failed_depth_count": 0,
                "usable_depth_ratio": 1.0,
                "fallback_coverage": "AVAILABLE",
            },
            {
                "exchange_id": "kucoin",
                "scan_failed": False,
                "verified_raw_only_count": 0,
                "depth_sampled_count": 0,
                "usable_depth_count": 0,
                "failed_depth_count": 0,
                "usable_depth_ratio": 0.0,
                "fallback_coverage": "NOT_REQUIRED",
            },
        ],
    }

    result = NativeCoveragePrioritizer().prioritize(
        scan_result["audits"]
    )

    priorities = result["priorities"]

    assert priorities[0]["exchange_id"] == "digifinex"
    assert priorities[0]["verified_raw_only_count"] == 513
    assert priorities[0]["depth_sampled_count"] == 20
    assert priorities[0]["usable_depth_count"] == 20
    assert priorities[0]["usable_depth_ratio"] == 1.0
    assert priorities[0]["implementation_status"] == "IMPLEMENTED"
    assert priorities[0]["implementation_required"] is False

    assert priorities[1]["exchange_id"] == "kucoin"
    assert priorities[1]["implementation_status"] == "NOT_REQUIRED"
    assert priorities[1]["implementation_required"] is False


def test_marks_uncovered_verified_exchange_for_implementation():
    audits = [
        {
            "exchange_id": "gate",
            "verified_raw_only_count": 75,
            "depth_sampled_count": 0,
            "usable_depth_count": 0,
            "usable_depth_ratio": 0.0,
            "fallback_coverage": "NOT_IMPLEMENTED",
        },
    ]

    result = NativeCoveragePrioritizer().prioritize(
        audits
    )

    priority = result["priorities"][0]

    assert priority[
        "implementation_status"
    ] == "NEEDS_IMPLEMENTATION"

    assert priority[
        "implementation_required"
    ] is True

    assert priority[
        "priority_reason"
    ] == (
        "unimplemented_native_coverage_"
        "without_depth_sample"
    )


def test_unimplemented_exchange_ranks_above_implemented_exchange():
    audits = [
        {
            "exchange_id": "digifinex",
            "verified_raw_only_count": 513,
            "depth_sampled_count": 20,
            "usable_depth_count": 20,
            "usable_depth_ratio": 1.0,
            "fallback_coverage": "AVAILABLE",
        },
        {
            "exchange_id": "gate",
            "verified_raw_only_count": 75,
            "depth_sampled_count": 0,
            "usable_depth_count": 0,
            "usable_depth_ratio": 0.0,
            "fallback_coverage": "NOT_IMPLEMENTED",
        },
    ]

    result = NativeCoveragePrioritizer().prioritize(
        audits
    )

    priorities = result["priorities"]

    assert priorities[0]["exchange_id"] == "gate"
    assert priorities[0]["implementation_status"] == (
        "NEEDS_IMPLEMENTATION"
    )

    assert priorities[1]["exchange_id"] == "digifinex"
    assert priorities[1]["implementation_status"] == (
        "IMPLEMENTED"
    )


def test_failed_exchange_never_outranks_healthy_candidate():
    audits = [
        {
            "exchange_id": "broken",
            "scan_failed": True,
            "verified_raw_only_count": 9999,
            "fallback_coverage": "NOT_IMPLEMENTED",
        },
        {
            "exchange_id": "gate",
            "scan_failed": False,
            "verified_raw_only_count": 25,
            "depth_sampled_count": 0,
            "usable_depth_count": 0,
            "usable_depth_ratio": 0.0,
            "fallback_coverage": "NOT_IMPLEMENTED",
        },
    ]

    result = NativeCoveragePrioritizer().prioritize(
        audits
    )

    assert len(result["priorities"]) == 1
    assert result["priorities"][0]["exchange_id"] == "gate"
    assert result["excluded_exchange_count"] == 1
