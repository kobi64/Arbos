import pytest

from core.broad_public_paper_scan_failure_diagnostics import (
    BroadPublicPaperScanFailureDiagnostics,
)


def test_healthy_when_no_failures_or_rejections():
    diagnostics = (
        BroadPublicPaperScanFailureDiagnostics()
    )

    result = diagnostics.build({
        "configured_exchange_count": 2,
        "discovered_exchange_count": 2,
        "discovery_failures": [],
        "scanner_failures": [],
        "rejected_routes": [],
    })

    assert result["status"] == "healthy"
    assert result["total_failure_count"] == 0
    assert result["rejected_route_count"] == 0


def test_degraded_when_failures_exist():
    diagnostics = (
        BroadPublicPaperScanFailureDiagnostics()
    )

    result = diagnostics.build({
        "configured_exchange_count": 2,
        "discovered_exchange_count": 2,
        "discovery_failures": [],
        "scanner_failures": [
            {
                "phase": "internal",
                "exchange_id": "gate",
                "coin_asset": "BTC",
                "reason": (
                    "internal_coin_scan_failed"
                ),
                "error": "RuntimeError: boom",
            },
        ],
        "rejected_routes": [],
    })

    assert result["status"] == "degraded"

    assert result[
        "failures_by_phase"
    ] == {
        "internal": 1,
    }

    assert result[
        "failures_by_exchange"
    ] == {
        "gate": 1,
    }

    assert result[
        "affected_coin_assets"
    ] == [
        "BTC",
    ]


def test_discovery_failure_is_classified():
    diagnostics = (
        BroadPublicPaperScanFailureDiagnostics()
    )

    result = diagnostics.build({
        "configured_exchange_count": 2,
        "discovered_exchange_count": 1,
        "discovery_failures": [
            {
                "exchange_id": "kucoin",
                "reason": (
                    "universe_discovery_failed"
                ),
                "error": "RuntimeError: unavailable",
            },
        ],
        "scanner_failures": [],
        "rejected_routes": [],
    })

    assert result[
        "failures_by_phase"
    ] == {
        "discovery": 1,
    }

    assert result[
        "failures_by_reason"
    ] == {
        "universe_discovery_failed": 1,
    }


def test_cross_exchange_failure_tracks_pair():
    diagnostics = (
        BroadPublicPaperScanFailureDiagnostics()
    )

    result = diagnostics.build({
        "configured_exchange_count": 2,
        "discovered_exchange_count": 2,
        "discovery_failures": [],
        "scanner_failures": [
            {
                "phase": "cross_exchange",
                "source_exchange_id": "gate",
                "destination_exchange_id": (
                    "kucoin"
                ),
                "coin_asset": "ETH",
                "reason": (
                    "cross_exchange_coin_scan_failed"
                ),
            },
        ],
        "rejected_routes": [],
    })

    assert result[
        "affected_exchange_pairs"
    ] == [
        {
            "source_exchange": "gate",
            "destination_exchange": "kucoin",
        },
    ]

    assert result[
        "failures_by_exchange"
    ] == {
        "gate": 1,
        "kucoin": 1,
    }


def test_rejection_reasons_are_counted():
    diagnostics = (
        BroadPublicPaperScanFailureDiagnostics()
    )

    result = diagnostics.build({
        "configured_exchange_count": 2,
        "discovered_exchange_count": 2,
        "discovery_failures": [],
        "scanner_failures": [],
        "rejected_routes": [
            {
                "reason": (
                    "transfer_verification_unavailable"
                ),
            },
            {
                "reason": (
                    "transfer_verification_unavailable"
                ),
            },
            {
                "reason": "network_unavailable",
            },
        ],
    })

    assert result["status"] == "degraded"

    assert result[
        "rejection_reasons"
    ] == {
        "network_unavailable": 1,
        "transfer_verification_unavailable": 2,
    }


def test_failed_when_no_exchange_discovery_succeeds():
    diagnostics = (
        BroadPublicPaperScanFailureDiagnostics()
    )

    result = diagnostics.build({
        "configured_exchange_count": 3,
        "discovered_exchange_count": 0,
        "discovery_failures": [
            {
                "exchange_id": "gate",
                "reason": (
                    "universe_discovery_failed"
                ),
            },
        ],
        "scanner_failures": [],
        "rejected_routes": [],
    })

    assert result["status"] == "failed"


def test_result_remains_paper_only():
    diagnostics = (
        BroadPublicPaperScanFailureDiagnostics()
    )

    result = diagnostics.build({})

    assert result["paper_only"] is True
    assert (
        result["live_order_submitted"]
        is False
    )


def test_scan_result_is_required():
    diagnostics = (
        BroadPublicPaperScanFailureDiagnostics()
    )

    with pytest.raises(
        ValueError,
        match="scan_result is required",
    ):
        diagnostics.build(None)
