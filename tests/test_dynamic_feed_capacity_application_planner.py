import pytest

from core.dynamic_feed_capacity_application_planner import (
    DynamicFeedCapacityApplicationPlanner,
)


def symbols(prefix, count):
    return [
        f"{prefix}{number}/USDT"
        for number in range(1, count + 1)
    ]


def test_scale_down_moves_excess_active_symbols_to_overflow():
    planner = DynamicFeedCapacityApplicationPlanner()

    active = symbols("COIN", 5)
    overflow = symbols("WAIT", 3)

    result = planner.plan(
        active_symbols=active,
        overflow_symbols=overflow,
        target_capacity=3,
    )

    assert result["action"] == "scale_down"

    assert result["active_symbols"] == [
        "COIN1/USDT",
        "COIN2/USDT",
        "COIN3/USDT",
    ]

    assert result["demoted_symbols"] == [
        "COIN4/USDT",
        "COIN5/USDT",
    ]

    assert result["overflow_symbols"] == [
        "COIN4/USDT",
        "COIN5/USDT",
        "WAIT1/USDT",
        "WAIT2/USDT",
        "WAIT3/USDT",
    ]


def test_scale_up_promotes_highest_priority_overflow_symbols():
    planner = DynamicFeedCapacityApplicationPlanner()

    result = planner.plan(
        active_symbols=symbols("COIN", 3),
        overflow_symbols=symbols("WAIT", 4),
        target_capacity=5,
    )

    assert result["action"] == "scale_up"

    assert result["promoted_symbols"] == [
        "WAIT1/USDT",
        "WAIT2/USDT",
    ]

    assert result["active_symbols"] == [
        "COIN1/USDT",
        "COIN2/USDT",
        "COIN3/USDT",
        "WAIT1/USDT",
        "WAIT2/USDT",
    ]

    assert result["overflow_symbols"] == [
        "WAIT3/USDT",
        "WAIT4/USDT",
    ]


def test_scale_up_is_limited_by_available_overflow():
    planner = DynamicFeedCapacityApplicationPlanner()

    result = planner.plan(
        active_symbols=symbols("COIN", 3),
        overflow_symbols=[
            "WAIT1/USDT",
        ],
        target_capacity=5,
    )

    assert result["action"] == "scale_up"

    assert result["active_symbol_count"] == 4

    assert result["promoted_symbols"] == [
        "WAIT1/USDT",
    ]


def test_equal_capacity_holds_existing_state():
    planner = DynamicFeedCapacityApplicationPlanner()

    result = planner.plan(
        active_symbols=symbols("COIN", 3),
        overflow_symbols=symbols("WAIT", 2),
        target_capacity=3,
    )

    assert result["action"] == "hold"
    assert result["changed"] is False

    assert result["active_symbols"] == (
        symbols("COIN", 3)
    )

    assert result["overflow_symbols"] == (
        symbols("WAIT", 2)
    )


def test_symbols_are_normalized_and_deduplicated():
    planner = DynamicFeedCapacityApplicationPlanner()

    result = planner.plan(
        active_symbols=[
            " btc/usdt ",
            "ETH/USDT",
            "BTC/USDT",
        ],
        overflow_symbols=[
            " xrp/usdt ",
            "XRP/USDT",
            " ada/usdt ",
        ],
        target_capacity=3,
    )

    assert result["active_symbols"] == [
        "BTC/USDT",
        "ETH/USDT",
        "XRP/USDT",
    ]

    assert result["overflow_symbols"] == [
        "ADA/USDT",
    ]


def test_active_symbols_are_required():
    planner = DynamicFeedCapacityApplicationPlanner()

    with pytest.raises(
        ValueError,
        match="active_symbols are required",
    ):
        planner.plan(
            active_symbols=[],
            overflow_symbols=[],
            target_capacity=1,
        )


def test_target_capacity_must_be_positive():
    planner = DynamicFeedCapacityApplicationPlanner()

    with pytest.raises(
        ValueError,
        match="target_capacity must be positive",
    ):
        planner.plan(
            active_symbols=[
                "BTC/USDT",
            ],
            overflow_symbols=[],
            target_capacity=0,
        )


def test_capacity_plan_is_paper_safe():
    planner = DynamicFeedCapacityApplicationPlanner()

    result = planner.plan(
        active_symbols=[
            "BTC/USDT",
        ],
        overflow_symbols=[],
        target_capacity=1,
    )

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False
