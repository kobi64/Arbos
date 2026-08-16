import pytest

from core.broad_public_paper_scan_summary import (
    BroadPublicPaperScanSummary,
)


def route(
    route_id,
    profit_percent,
    *,
    route_type="internal_triangle",
    executable=True,
):
    return {
        "route_id": route_id,
        "route_type": route_type,
        "coin_asset": "BTC",
        "source_exchange": "gate",
        "destination_exchange": (
            "kucoin"
            if route_type
            == "direct_cross_exchange"
            else None
        ),
        "net_profit": profit_percent,
        "net_profit_percent": (
            profit_percent
        ),
        "max_leg_slippage_percent": 0.01,
        "executable": executable,
    }


def test_builds_operator_summary():
    summary = BroadPublicPaperScanSummary()

    result = summary.build({
        "ranked_routes": [
            route("A", 1.2),
            route("B", -0.3),
            route(
                "C",
                0.8,
                route_type=(
                    "direct_cross_exchange"
                ),
            ),
        ],
        "rejected_routes": [
            {
                "reason": (
                    "transfer_verification_unavailable"
                ),
            },
        ],
        "route_count": 3,
        "internal_route_count": 2,
        "cross_exchange_route_count": 1,
        "successful_internal_scans": 4,
        "successful_cross_exchange_scans": 2,
        "unique_coin_count": 2,
        "unique_coin_assets": [
            "BTC",
            "ETH",
        ],
        "rejected_count": 1,
    })

    assert result[
        "profitable_route_count"
    ] == 2

    assert result[
        "unprofitable_route_count"
    ] == 1

    assert result[
        "best_route"
    ]["route_id"] == "A"

    assert [
        item["route_id"]
        for item in result[
            "top_profitable_routes"
        ]
    ] == [
        "A",
        "C",
    ]

    assert result[
        "rejection_reasons"
    ] == {
        "transfer_verification_unavailable": 1,
    }


def test_top_limit_is_applied():
    summary = BroadPublicPaperScanSummary()

    result = summary.build(
        {
            "ranked_routes": [
                route("A", 3.0),
                route("B", 2.0),
                route("C", 1.0),
            ],
        },
        top_limit=2,
    )

    assert [
        item["route_id"]
        for item in result[
            "top_profitable_routes"
        ]
    ] == [
        "A",
        "B",
    ]


def test_rejection_reasons_are_counted():
    summary = BroadPublicPaperScanSummary()

    result = summary.build({
        "ranked_routes": [],
        "rejected_routes": [
            {"reason": "network_unavailable"},
            {"reason": "network_unavailable"},
            {
                "reason": (
                    "transfer_verification_unavailable"
                ),
            },
        ],
    })

    assert result[
        "rejection_reasons"
    ] == {
        "network_unavailable": 2,
        "transfer_verification_unavailable": 1,
    }


def test_summary_remains_paper_only():
    summary = BroadPublicPaperScanSummary()

    result = summary.build({
        "ranked_routes": [],
    })

    assert result["paper_only"] is True
    assert (
        result["live_order_submitted"]
        is False
    )


def test_scan_result_is_required():
    summary = BroadPublicPaperScanSummary()

    with pytest.raises(
        ValueError,
        match="scan_result is required",
    ):
        summary.build(None)


@pytest.mark.parametrize(
    "top_limit",
    [
        0,
        -1,
        True,
    ],
)
def test_top_limit_must_be_positive_integer(
    top_limit,
):
    summary = BroadPublicPaperScanSummary()

    with pytest.raises(
        ValueError,
        match="top_limit must be positive",
    ):
        summary.build(
            {},
            top_limit=top_limit,
        )
