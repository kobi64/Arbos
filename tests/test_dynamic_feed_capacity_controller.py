import pytest

from core.dynamic_feed_capacity_controller import (
    DynamicFeedCapacityController,
)


def profile():
    return {
        "exchange_id": "kucoin",
        "max_symbols_per_batch": 80,
        "max_batches": 4,
        "max_total_symbols": 320,
    }


def healthy_snapshot(symbol_count):
    return {
        "symbol_count": symbol_count,
        "healthy_symbol_count": symbol_count,
        "unhealthy_symbol_count": 0,
        "unhealthy_symbols": [],
    }


def unhealthy_snapshot(
    symbol_count,
    unhealthy_count=1,
):
    return {
        "symbol_count": symbol_count,
        "healthy_symbol_count": (
            symbol_count
            - unhealthy_count
        ),
        "unhealthy_symbol_count": (
            unhealthy_count
        ),
        "unhealthy_symbols": [
            f"BAD{i}/USDT"
            for i in range(
                unhealthy_count
            )
        ],
    }


def test_scales_up_one_batch_when_feed_is_healthy():
    controller = DynamicFeedCapacityController(
        profile=profile()
    )

    result = controller.decide(
        current_capacity=160,
        health_snapshot=healthy_snapshot(
            160
        ),
    )

    assert result["action"] == "scale_up"
    assert result["current_capacity"] == 160
    assert result["target_capacity"] == 240
    assert result["capacity_change"] == 80


def test_scale_up_never_exceeds_profile_maximum():
    controller = DynamicFeedCapacityController(
        profile=profile()
    )

    result = controller.decide(
        current_capacity=280,
        health_snapshot=healthy_snapshot(
            280
        ),
    )

    assert result["target_capacity"] == 320
    assert result["capacity_change"] == 40


def test_holds_when_healthy_and_already_at_maximum():
    controller = DynamicFeedCapacityController(
        profile=profile()
    )

    result = controller.decide(
        current_capacity=320,
        health_snapshot=healthy_snapshot(
            320
        ),
    )

    assert result["action"] == "hold"
    assert result["target_capacity"] == 320
    assert result["capacity_change"] == 0


def test_scales_down_one_batch_when_feed_is_unhealthy():
    controller = DynamicFeedCapacityController(
        profile=profile()
    )

    result = controller.decide(
        current_capacity=320,
        health_snapshot=unhealthy_snapshot(
            320,
            unhealthy_count=3,
        ),
    )

    assert result["action"] == "scale_down"
    assert result["current_capacity"] == 320
    assert result["target_capacity"] == 240
    assert result["capacity_change"] == -80


def test_scale_down_never_goes_below_one_batch():
    controller = DynamicFeedCapacityController(
        profile=profile()
    )

    result = controller.decide(
        current_capacity=80,
        health_snapshot=unhealthy_snapshot(
            80
        ),
    )

    assert result["action"] == "hold"
    assert result["target_capacity"] == 80
    assert result["capacity_change"] == 0


def test_partial_batch_capacity_can_scale_down_safely():
    controller = DynamicFeedCapacityController(
        profile=profile()
    )

    result = controller.decide(
        current_capacity=100,
        health_snapshot=unhealthy_snapshot(
            100
        ),
    )

    assert result["target_capacity"] == 80
    assert result["capacity_change"] == -20


def test_profile_is_required():
    with pytest.raises(
        ValueError,
        match="profile is required",
    ):
        DynamicFeedCapacityController(
            profile=None
        )


def test_current_capacity_must_be_positive():
    controller = DynamicFeedCapacityController(
        profile=profile()
    )

    with pytest.raises(
        ValueError,
        match="current_capacity must be positive",
    ):
        controller.decide(
            current_capacity=0,
            health_snapshot=healthy_snapshot(
                0
            ),
        )


def test_health_snapshot_is_required():
    controller = DynamicFeedCapacityController(
        profile=profile()
    )

    with pytest.raises(
        ValueError,
        match="health_snapshot is required",
    ):
        controller.decide(
            current_capacity=80,
            health_snapshot=None,
        )


def test_capacity_decision_is_paper_safe():
    controller = DynamicFeedCapacityController(
        profile=profile()
    )

    result = controller.decide(
        current_capacity=80,
        health_snapshot=healthy_snapshot(
            80
        ),
    )

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_transient_single_unhealthy_snapshot_does_not_scale_down():
    controller = DynamicFeedCapacityController(
        profile=profile(),
        unhealthy_confirmations=2,
        healthy_confirmations=3,
    )

    result = controller.decide(
        current_capacity=320,
        health_snapshot=unhealthy_snapshot(
            320
        ),
    )

    assert result["action"] == "hold"
    assert result["target_capacity"] == 320
    assert result[
        "consecutive_unhealthy"
    ] == 1


def test_second_consecutive_unhealthy_snapshot_scales_down():
    controller = DynamicFeedCapacityController(
        profile=profile(),
        unhealthy_confirmations=2,
        healthy_confirmations=3,
    )

    controller.decide(
        current_capacity=320,
        health_snapshot=unhealthy_snapshot(
            320
        ),
    )

    result = controller.decide(
        current_capacity=320,
        health_snapshot=unhealthy_snapshot(
            320
        ),
    )

    assert result["action"] == "scale_down"
    assert result["target_capacity"] == 240


def test_recovery_requires_multiple_healthy_snapshots():
    controller = DynamicFeedCapacityController(
        profile=profile(),
        unhealthy_confirmations=2,
        healthy_confirmations=3,
    )

    first = controller.decide(
        current_capacity=240,
        health_snapshot=healthy_snapshot(
            240
        ),
    )

    second = controller.decide(
        current_capacity=240,
        health_snapshot=healthy_snapshot(
            240
        ),
    )

    third = controller.decide(
        current_capacity=240,
        health_snapshot=healthy_snapshot(
            240
        ),
    )

    assert first["action"] == "hold"
    assert second["action"] == "hold"
    assert third["action"] == "scale_up"

    assert third["target_capacity"] == 320


def test_health_direction_change_resets_confirmation_counter():
    controller = DynamicFeedCapacityController(
        profile=profile(),
        unhealthy_confirmations=2,
        healthy_confirmations=3,
    )

    controller.decide(
        current_capacity=320,
        health_snapshot=unhealthy_snapshot(
            320
        ),
    )

    healthy = controller.decide(
        current_capacity=320,
        health_snapshot=healthy_snapshot(
            320
        ),
    )

    assert healthy[
        "consecutive_unhealthy"
    ] == 0

    assert healthy[
        "consecutive_healthy"
    ] == 1


def test_confirmation_thresholds_must_be_positive():
    with pytest.raises(
        ValueError,
        match="unhealthy_confirmations must be positive",
    ):
        DynamicFeedCapacityController(
            profile=profile(),
            unhealthy_confirmations=0,
        )

    with pytest.raises(
        ValueError,
        match="healthy_confirmations must be positive",
    ):
        DynamicFeedCapacityController(
            profile=profile(),
            healthy_confirmations=0,
        )


@pytest.mark.parametrize(
    "snapshot",
    [
        {},
        {"unhealthy_symbol_count": None},
    ],
)
def test_missing_unhealthy_count_is_rejected(snapshot):
    controller = DynamicFeedCapacityController(
        profile=profile()
    )

    with pytest.raises(
        ValueError,
        match="unhealthy_symbol_count is required",
    ):
        controller.decide(
            current_capacity=160,
            health_snapshot=snapshot,
        )


@pytest.mark.parametrize(
    "value",
    [
        "not-a-number",
        -1,
        1.5,
        "1.5",
        True,
    ],
)
def test_invalid_unhealthy_count_is_rejected(value):
    controller = DynamicFeedCapacityController(
        profile=profile()
    )

    with pytest.raises(
        ValueError,
        match="unhealthy_symbol_count must be a non-negative integer",
    ):
        controller.decide(
            current_capacity=160,
            health_snapshot={
                "unhealthy_symbol_count": value,
            },
        )


def test_explicit_zero_unhealthy_count_remains_healthy():
    controller = DynamicFeedCapacityController(
        profile=profile()
    )

    result = controller.decide(
        current_capacity=160,
        health_snapshot={
            "unhealthy_symbol_count": 0,
        },
    )

    assert result["unhealthy_symbol_count"] == 0
    assert result["action"] == "scale_up"
