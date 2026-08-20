import pytest

from core.hundred_coin_paper_scan_readiness import (
    HundredCoinPaperScanReadiness,
)


def evaluate(
    exchange_coin_assets,
    requested_coin_count=3,
):
    return (
        HundredCoinPaperScanReadiness()
        .evaluate(
            exchange_coin_assets=(
                exchange_coin_assets
            ),
            requested_coin_count=(
                requested_coin_count
            ),
        )
    )


def test_selects_globally_bounded_universe():
    result = evaluate({
        "kucoin": {
            "BTC",
            "ETH",
            "SOL",
            "XRP",
        },
        "gate": {
            "BTC",
            "ETH",
            "SOL",
            "DOGE",
        },
        "bitget": {
            "BTC",
            "ETH",
            "XRP",
        },
    })

    assert result["ready"] is True
    assert result["readiness"] == "PASS"
    assert result[
        "selected_coin_count"
    ] == 3

    assert result[
        "selected_coin_assets"
    ] == [
        "BTC",
        "ETH",
        "SOL",
    ]


def test_prefers_greater_exchange_coverage():
    result = evaluate(
        {
            "a": {
                "BTC",
                "ETH",
                "SOL",
            },
            "b": {
                "BTC",
                "ETH",
                "SOL",
            },
            "c": {
                "BTC",
                "ETH",
            },
        },
        requested_coin_count=2,
    )

    assert result[
        "selected_coin_assets"
    ] == [
        "BTC",
        "ETH",
    ]


def test_requires_cross_exchange_coverage():
    result = evaluate(
        {
            "a": {
                "BTC",
                "ONLYA",
            },
            "b": {
                "BTC",
                "ONLYB",
            },
        },
        requested_coin_count=2,
    )

    assert result["ready"] is False
    assert result["readiness"] == "FAIL"
    assert result["reason"] == (
        "insufficient_cross_exchange_coin_coverage"
    )
    assert result[
        "selected_coin_assets"
    ] == [
        "BTC",
    ]


def test_selected_assets_are_mapped_per_exchange():
    result = evaluate({
        "kucoin": {
            "BTC",
            "ETH",
            "SOL",
        },
        "gate": {
            "BTC",
            "ETH",
            "SOL",
        },
        "bitget": {
            "BTC",
            "ETH",
        },
    })

    assert result[
        "exchange_selected_assets"
    ]["kucoin"] == [
        "BTC",
        "ETH",
        "SOL",
    ]

    assert result[
        "exchange_selected_assets"
    ]["bitget"] == [
        "BTC",
        "ETH",
    ]


def test_rejected_single_exchange_coin_is_reported():
    result = evaluate(
        {
            "kucoin": {
                "BTC",
                "ETH",
                "ONLYK",
            },
            "gate": {
                "BTC",
                "ETH",
            },
        },
        requested_coin_count=2,
    )

    rejected = {
        item["coin_asset"]
        for item in result[
            "rejected_coins"
        ]
    }

    assert rejected == {
        "ONLYK",
    }


def test_normalizes_exchange_and_coin_names():
    result = evaluate(
        {
            " KUCOIN ": {
                " btc ",
                " eth ",
            },
            "Gate": {
                "BTC",
                "ETH",
            },
        },
        requested_coin_count=2,
    )

    assert result[
        "selected_coin_assets"
    ] == [
        "BTC",
        "ETH",
    ]

    assert set(
        result[
            "exchange_selected_assets"
        ]
    ) == {
        "kucoin",
        "gate",
    }


def test_duplicate_coin_values_do_not_inflate_coverage():
    result = evaluate(
        {
            "a": [
                "BTC",
                "BTC",
                "ETH",
            ],
            "b": [
                "BTC",
                "ETH",
            ],
        },
        requested_coin_count=2,
    )

    btc = next(
        item
        for item in result[
            "coverage_records"
        ]
        if item["coin_asset"] == "BTC"
    )

    assert btc["exchange_count"] == 2


def test_result_is_strictly_paper_only():
    result = evaluate(
        {
            "a": {
                "BTC",
                "ETH",
                "SOL",
            },
            "b": {
                "BTC",
                "ETH",
                "SOL",
            },
        }
    )

    assert result["paper_only"] is True
    assert (
        result["live_order_submitted"]
        is False
    )


@pytest.mark.parametrize(
    "value",
    [
        0,
        -1,
        True,
        1.5,
    ],
)
def test_requested_coin_count_must_be_positive_integer(
    value,
):
    with pytest.raises(
        ValueError,
        match=(
            "requested_coin_count "
            "must be positive"
        ),
    ):
        (
            HundredCoinPaperScanReadiness()
            .evaluate(
                exchange_coin_assets={
                    "a": {"BTC"},
                    "b": {"BTC"},
                },
                requested_coin_count=value,
            )
        )


@pytest.mark.parametrize(
    "value",
    [
        0,
        1,
        True,
        1.5,
    ],
)
def test_minimum_exchange_coverage_must_be_at_least_two(
    value,
):
    with pytest.raises(
        ValueError,
        match=(
            "minimum_exchange_coverage "
            "must be at least 2"
        ),
    ):
        (
            HundredCoinPaperScanReadiness()
            .evaluate(
                exchange_coin_assets={
                    "a": {"BTC"},
                    "b": {"BTC"},
                },
                requested_coin_count=1,
                minimum_exchange_coverage=(
                    value
                ),
            )
        )


def test_requires_two_exchanges():
    with pytest.raises(
        ValueError,
        match=(
            "at least two exchanges "
            "are required"
        ),
    ):
        (
            HundredCoinPaperScanReadiness()
            .evaluate(
                exchange_coin_assets={
                    "kucoin": {
                        "BTC",
                    },
                },
                requested_coin_count=1,
            )
        )
