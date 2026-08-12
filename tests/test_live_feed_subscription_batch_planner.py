import pytest

from core.live_feed_subscription_batch_planner import (
    LiveFeedSubscriptionBatchPlanner,
)


def test_splits_symbols_into_configured_batches():
    planner = LiveFeedSubscriptionBatchPlanner(
        max_symbols_per_batch=3,
        max_batches=10,
    )

    result = planner.plan(
        exchange_id="kucoin",
        symbols=[
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
            "XRP/USDT",
            "DOGE/USDT",
            "ADA/USDT",
            "AVAX/USDT",
        ],
    )

    assert result["exchange_id"] == "kucoin"

    assert result["batches"] == [
        [
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
        ],
        [
            "XRP/USDT",
            "DOGE/USDT",
            "ADA/USDT",
        ],
        [
            "AVAX/USDT",
        ],
    ]

    assert result["batch_count"] == 3
    assert result["selected_symbol_count"] == 7
    assert result["overflow_symbol_count"] == 0


def test_normalizes_and_deduplicates_symbols():
    planner = LiveFeedSubscriptionBatchPlanner(
        max_symbols_per_batch=10,
        max_batches=10,
    )

    result = planner.plan(
        exchange_id=" KUCOIN ",
        symbols=[
            " btc/usdt ",
            "BTC/USDT",
            "eth/usdt",
        ],
    )

    assert result["exchange_id"] == "kucoin"

    assert result["batches"] == [
        [
            "BTC/USDT",
            "ETH/USDT",
        ],
    ]


def test_respects_total_exchange_subscription_cap():
    planner = LiveFeedSubscriptionBatchPlanner(
        max_symbols_per_batch=2,
        max_batches=2,
    )

    result = planner.plan(
        exchange_id="gate",
        symbols=[
            "A/USDT",
            "B/USDT",
            "C/USDT",
            "D/USDT",
            "E/USDT",
        ],
    )

    assert result["selected_symbol_count"] == 4
    assert result["overflow_symbol_count"] == 1

    assert result["overflow_symbols"] == [
        "E/USDT",
    ]


def test_preserves_input_priority_order():
    planner = LiveFeedSubscriptionBatchPlanner(
        max_symbols_per_batch=2,
        max_batches=2,
    )

    result = planner.plan(
        exchange_id="htx",
        symbols=[
            "HIGH1/USDT",
            "HIGH2/USDT",
            "MID/USDT",
            "LOW/USDT",
            "EXTRA/USDT",
        ],
    )

    assert result["selected_symbols"] == [
        "HIGH1/USDT",
        "HIGH2/USDT",
        "MID/USDT",
        "LOW/USDT",
    ]

    assert result["overflow_symbols"] == [
        "EXTRA/USDT",
    ]


def test_empty_symbols_are_rejected():
    planner = LiveFeedSubscriptionBatchPlanner(
        max_symbols_per_batch=10,
        max_batches=10,
    )

    with pytest.raises(
        ValueError,
        match="symbols are required",
    ):
        planner.plan(
            exchange_id="kucoin",
            symbols=[],
        )


def test_exchange_id_is_required():
    planner = LiveFeedSubscriptionBatchPlanner(
        max_symbols_per_batch=10,
        max_batches=10,
    )

    with pytest.raises(
        ValueError,
        match="exchange_id is required",
    ):
        planner.plan(
            exchange_id="",
            symbols=[
                "BTC/USDT",
            ],
        )


def test_batch_limits_must_be_positive():
    with pytest.raises(
        ValueError,
        match="max_symbols_per_batch must be positive",
    ):
        LiveFeedSubscriptionBatchPlanner(
            max_symbols_per_batch=0,
            max_batches=1,
        )

    with pytest.raises(
        ValueError,
        match="max_batches must be positive",
    ):
        LiveFeedSubscriptionBatchPlanner(
            max_symbols_per_batch=10,
            max_batches=0,
        )


def test_planner_is_paper_safe():
    planner = LiveFeedSubscriptionBatchPlanner(
        max_symbols_per_batch=10,
        max_batches=10,
    )

    result = planner.plan(
        exchange_id="bitget",
        symbols=[
            "BTC/USDT",
        ],
    )

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_builds_planner_from_exchange_profile():
    profile = {
        "exchange_id": "kucoin",
        "max_symbols_per_batch": 3,
        "max_batches": 2,
        "max_total_symbols": 6,
    }

    planner = (
        LiveFeedSubscriptionBatchPlanner
        .from_profile(profile)
    )

    result = planner.plan(
        exchange_id="kucoin",
        symbols=[
            "A/USDT",
            "B/USDT",
            "C/USDT",
            "D/USDT",
            "E/USDT",
            "F/USDT",
            "G/USDT",
        ],
    )

    assert result[
        "selected_symbol_count"
    ] == 6

    assert result[
        "overflow_symbols"
    ] == [
        "G/USDT",
    ]


def test_from_profile_requires_profile():
    import pytest

    with pytest.raises(
        ValueError,
        match="profile is required",
    ):
        (
            LiveFeedSubscriptionBatchPlanner
            .from_profile(None)
        )


def test_from_profile_uses_profile_limits():
    profile = {
        "exchange_id": "gate",
        "max_symbols_per_batch": 2,
        "max_batches": 3,
    }

    planner = (
        LiveFeedSubscriptionBatchPlanner
        .from_profile(profile)
    )

    result = planner.plan(
        exchange_id="gate",
        symbols=[
            "A/USDT",
            "B/USDT",
            "C/USDT",
            "D/USDT",
            "E/USDT",
            "F/USDT",
            "G/USDT",
        ],
    )

    assert result[
        "max_symbols_per_batch"
    ] == 2

    assert result[
        "max_batches"
    ] == 3

    assert result[
        "capacity"
    ] == 6
