import pytest

from core.exchange_subscription_capacity_profiles import (
    ExchangeSubscriptionCapacityProfiles,
)
from core.hundred_coin_feed_capacity_readiness import (
    HundredCoinFeedCapacityReadiness,
)


def profiles(
    *,
    kucoin_capacity=4,
    gate_capacity=4,
):
    registry = (
        ExchangeSubscriptionCapacityProfiles()
    )

    for exchange_id, capacity in (
        ("kucoin", kucoin_capacity),
        ("gate", gate_capacity),
    ):
        registry.register({
            "exchange_id": exchange_id,
            "max_symbols_per_batch": 2,
            "max_batches": (
                capacity // 2
            ),
        })

    return registry


def test_capacity_passes_when_all_symbols_fit():
    result = (
        HundredCoinFeedCapacityReadiness()
        .evaluate(
            exchange_selected_assets={
                "kucoin": [
                    "BTC",
                    "ETH",
                    "SOL",
                ],
                "gate": [
                    "BTC",
                    "ETH",
                ],
            },
            capacity_profiles=profiles(),
        )
    )

    assert result["ready"] is True
    assert result["readiness"] == "PASS"
    assert result["reason"] is None
    assert result[
        "total_required_symbol_count"
    ] == 5
    assert result[
        "total_selected_symbol_count"
    ] == 5
    assert result[
        "total_overflow_symbol_count"
    ] == 0


def test_maps_assets_to_usdt_symbols():
    result = (
        HundredCoinFeedCapacityReadiness()
        .evaluate(
            exchange_selected_assets={
                "kucoin": [
                    "btc",
                    " eth ",
                ],
                "gate": [
                    "BTC",
                    "ETH",
                ],
            },
            capacity_profiles=profiles(),
        )
    )

    assert result[
        "exchange_plans"
    ]["kucoin"][
        "selected_symbols"
    ] == [
        "BTC/USDT",
        "ETH/USDT",
    ]


def test_capacity_fails_closed_on_overflow():
    result = (
        HundredCoinFeedCapacityReadiness()
        .evaluate(
            exchange_selected_assets={
                "kucoin": [
                    "BTC",
                    "ETH",
                    "SOL",
                ],
                "gate": [
                    "BTC",
                    "ETH",
                ],
            },
            capacity_profiles=profiles(
                kucoin_capacity=2,
            ),
        )
    )

    assert result["ready"] is False
    assert result["readiness"] == "FAIL"
    assert result["reason"] == (
        "feed_capacity_exceeded"
    )
    assert result[
        "total_overflow_symbol_count"
    ] == 1

    failure = result["failures"][0]

    assert failure["exchange_id"] == (
        "kucoin"
    )
    assert failure["reason"] == (
        "feed_capacity_exceeded"
    )
    assert failure[
        "overflow_symbols"
    ] == [
        "SOL/USDT",
    ]


def test_missing_capacity_profile_fails_closed():
    registry = (
        ExchangeSubscriptionCapacityProfiles()
    )

    registry.register({
        "exchange_id": "kucoin",
        "max_symbols_per_batch": 10,
        "max_batches": 1,
    })

    result = (
        HundredCoinFeedCapacityReadiness()
        .evaluate(
            exchange_selected_assets={
                "kucoin": [
                    "BTC",
                ],
                "gate": [
                    "BTC",
                ],
            },
            capacity_profiles=registry,
        )
    )

    assert result["ready"] is False
    assert result["reason"] == (
        "capacity_profile_unavailable"
    )

    assert result["failures"] == [
        {
            "exchange_id": "gate",
            "reason": (
                "capacity_profile_unavailable"
            ),
            "required_symbol_count": 1,
        },
    ]


def test_duplicate_assets_do_not_inflate_required_count():
    result = (
        HundredCoinFeedCapacityReadiness()
        .evaluate(
            exchange_selected_assets={
                "kucoin": [
                    "BTC",
                    "btc",
                    "ETH",
                ],
                "gate": [
                    "BTC",
                    "ETH",
                ],
            },
            capacity_profiles=profiles(),
        )
    )

    assert result[
        "total_required_symbol_count"
    ] == 4


def test_blank_exchange_and_assets_are_ignored():
    result = (
        HundredCoinFeedCapacityReadiness()
        .evaluate(
            exchange_selected_assets={
                "": [
                    "BTC",
                ],
                "kucoin": [
                    "",
                    "BTC",
                ],
                "gate": [
                    "BTC",
                ],
            },
            capacity_profiles=profiles(),
        )
    )

    assert result["ready"] is True
    assert result[
        "planned_exchange_count"
    ] == 2


def test_result_is_strictly_paper_only():
    result = (
        HundredCoinFeedCapacityReadiness()
        .evaluate(
            exchange_selected_assets={
                "kucoin": ["BTC"],
                "gate": ["BTC"],
            },
            capacity_profiles=profiles(),
        )
    )

    assert result["paper_only"] is True
    assert (
        result["live_order_submitted"]
        is False
    )

    for plan in result[
        "exchange_plans"
    ].values():
        assert plan["paper_only"] is True
        assert (
            plan["live_order_submitted"]
            is False
        )


def test_exchange_assets_mapping_is_required():
    with pytest.raises(
        ValueError,
        match=(
            "exchange_selected_assets "
            "are required"
        ),
    ):
        (
            HundredCoinFeedCapacityReadiness()
            .evaluate(
                exchange_selected_assets=None,
                capacity_profiles=profiles(),
            )
        )


def test_capacity_profiles_are_required():
    with pytest.raises(
        ValueError,
        match="capacity_profiles are required",
    ):
        (
            HundredCoinFeedCapacityReadiness()
            .evaluate(
                exchange_selected_assets={
                    "kucoin": ["BTC"],
                    "gate": ["BTC"],
                },
                capacity_profiles=None,
            )
        )


def test_no_exchange_symbols_are_rejected():
    with pytest.raises(
        ValueError,
        match=(
            "no exchange symbols are available"
        ),
    ):
        (
            HundredCoinFeedCapacityReadiness()
            .evaluate(
                exchange_selected_assets={
                    "kucoin": [],
                    "gate": [],
                },
                capacity_profiles=profiles(),
            )
        )
