import pytest

from core.live_feed_subscription_rotation_planner import (
    LiveFeedSubscriptionRotationPlanner,
)


def test_replaces_unhealthy_symbol_with_first_overflow_symbol():
    planner = LiveFeedSubscriptionRotationPlanner()

    result = planner.plan(
        active_symbols=[
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
        ],
        unhealthy_symbols=[
            "ETH/USDT",
        ],
        overflow_symbols=[
            "XRP/USDT",
            "ADA/USDT",
        ],
    )

    assert result["retained_symbols"] == [
        "BTC/USDT",
        "SOL/USDT",
    ]

    assert result["removed_symbols"] == [
        "ETH/USDT",
    ]

    assert result["promoted_symbols"] == [
        "XRP/USDT",
    ]

    assert result["active_symbols"] == [
        "BTC/USDT",
        "SOL/USDT",
        "XRP/USDT",
    ]

    assert result["overflow_symbols"] == [
        "ADA/USDT",
    ]


def test_multiple_unhealthy_symbols_promote_in_priority_order():
    planner = LiveFeedSubscriptionRotationPlanner()

    result = planner.plan(
        active_symbols=[
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
            "DOGE/USDT",
        ],
        unhealthy_symbols=[
            "ETH/USDT",
            "DOGE/USDT",
        ],
        overflow_symbols=[
            "XRP/USDT",
            "ADA/USDT",
            "AVAX/USDT",
        ],
    )

    assert result["removed_symbols"] == [
        "ETH/USDT",
        "DOGE/USDT",
    ]

    assert result["promoted_symbols"] == [
        "XRP/USDT",
        "ADA/USDT",
    ]

    assert result["active_symbols"] == [
        "BTC/USDT",
        "SOL/USDT",
        "XRP/USDT",
        "ADA/USDT",
    ]

    assert result["overflow_symbols"] == [
        "AVAX/USDT",
    ]


def test_no_unhealthy_symbols_produces_no_rotation():
    planner = LiveFeedSubscriptionRotationPlanner()

    result = planner.plan(
        active_symbols=[
            "BTC/USDT",
            "ETH/USDT",
        ],
        unhealthy_symbols=[],
        overflow_symbols=[
            "XRP/USDT",
        ],
    )

    assert result["rotation_required"] is False

    assert result["active_symbols"] == [
        "BTC/USDT",
        "ETH/USDT",
    ]

    assert result["overflow_symbols"] == [
        "XRP/USDT",
    ]

    assert result["removed_symbols"] == []
    assert result["promoted_symbols"] == []


def test_unhealthy_symbol_is_removed_even_without_replacement():
    planner = LiveFeedSubscriptionRotationPlanner()

    result = planner.plan(
        active_symbols=[
            "BTC/USDT",
            "ETH/USDT",
        ],
        unhealthy_symbols=[
            "ETH/USDT",
        ],
        overflow_symbols=[],
    )

    assert result["rotation_required"] is True

    assert result["removed_symbols"] == [
        "ETH/USDT",
    ]

    assert result["promoted_symbols"] == []

    assert result["active_symbols"] == [
        "BTC/USDT",
    ]


def test_unknown_unhealthy_symbol_does_not_remove_active_symbol():
    planner = LiveFeedSubscriptionRotationPlanner()

    result = planner.plan(
        active_symbols=[
            "BTC/USDT",
            "ETH/USDT",
        ],
        unhealthy_symbols=[
            "UNKNOWN/USDT",
        ],
        overflow_symbols=[
            "XRP/USDT",
        ],
    )

    assert result["rotation_required"] is False

    assert result["removed_symbols"] == []

    assert result["promoted_symbols"] == []

    assert result["active_symbols"] == [
        "BTC/USDT",
        "ETH/USDT",
    ]


def test_symbols_are_normalized_and_deduplicated():
    planner = LiveFeedSubscriptionRotationPlanner()

    result = planner.plan(
        active_symbols=[
            " btc/usdt ",
            "ETH/USDT",
            "BTC/USDT",
        ],
        unhealthy_symbols=[
            " eth/usdt ",
        ],
        overflow_symbols=[
            " xrp/usdt ",
            "XRP/USDT",
            " ada/usdt ",
        ],
    )

    assert result["removed_symbols"] == [
        "ETH/USDT",
    ]

    assert result["promoted_symbols"] == [
        "XRP/USDT",
    ]

    assert result["active_symbols"] == [
        "BTC/USDT",
        "XRP/USDT",
    ]

    assert result["overflow_symbols"] == [
        "ADA/USDT",
    ]


def test_active_symbols_are_required():
    planner = LiveFeedSubscriptionRotationPlanner()

    with pytest.raises(
        ValueError,
        match="active_symbols are required",
    ):
        planner.plan(
            active_symbols=[],
            unhealthy_symbols=[],
            overflow_symbols=[],
        )


def test_rotation_plan_is_paper_safe():
    planner = LiveFeedSubscriptionRotationPlanner()

    result = planner.plan(
        active_symbols=[
            "BTC/USDT",
        ],
        unhealthy_symbols=[],
        overflow_symbols=[],
    )

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False
