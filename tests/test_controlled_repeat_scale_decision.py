import pytest

from core.controlled_repeat_scale_decision import (
    ControlledRepeatScaleDecision,
)


def successful_validation():
    return {
        "validated": True,
        "accepted": True,
        "reason": "simulated_route_validation_passed",
        "route_id": "ROUTE-001",
        "approval_id": "ARB-001",
        "permission_id": "PERM-001",
        "net_profit": 4.0,
        "profit_percent": 1.6,
        "test_trade": True,
        "simulated": True,
        "paper_trade": True,
        "live_order_submitted": False,
    }


def decide(
    validation_result=None,
    current_trade_size=250.0,
    successful_test_count=1,
    required_successes_for_scale=2,
    scale_multiplier=2.0,
    min_trade_size=10.0,
    max_trade_size=1000.0,
):
    controller = ControlledRepeatScaleDecision()

    return controller.decide(
        validation_result=(
            successful_validation()
            if validation_result is None
            else validation_result
        ),
        current_trade_size=current_trade_size,
        successful_test_count=successful_test_count,
        required_successes_for_scale=(
            required_successes_for_scale
        ),
        scale_multiplier=scale_multiplier,
        min_trade_size=min_trade_size,
        max_trade_size=max_trade_size,
    )


def test_requires_more_successes_before_scaling():
    result = decide(
        successful_test_count=1,
        required_successes_for_scale=2,
    )

    assert result["decision"] == "REPEAT_SAME_SIZE"
    assert result["allowed"] is True
    assert result["next_trade_size"] == 250.0
    assert result["scale_applied"] is False


def test_scales_after_required_successes():
    result = decide(
        successful_test_count=2,
        required_successes_for_scale=2,
    )

    assert result["decision"] == "SCALE_UP"
    assert result["allowed"] is True
    assert result["next_trade_size"] == 500.0
    assert result["scale_applied"] is True


def test_scale_multiplier_is_applied():
    result = decide(
        current_trade_size=200.0,
        successful_test_count=3,
        required_successes_for_scale=2,
        scale_multiplier=1.5,
    )

    assert result["next_trade_size"] == 300.0


def test_scale_above_max_repeats_same_size():
    result = decide(
        current_trade_size=600.0,
        successful_test_count=2,
        required_successes_for_scale=2,
        scale_multiplier=2.0,
        max_trade_size=1000.0,
    )

    assert result["decision"] == "REPEAT_SAME_SIZE"
    assert result["next_trade_size"] == 600.0
    assert result["proposed_trade_size"] == 1200.0
    assert result["reason"] == "scale_limit_reached"
    assert result["trade_size_reason"] == "above_maximum"
    assert result["scale_applied"] is False


def test_rejected_validation_stops():
    record = successful_validation()
    record["accepted"] = False

    result = decide(
        validation_result=record
    )

    assert result["decision"] == "STOP"
    assert result["allowed"] is False
    assert (
        result["reason"]
        == "successful_test_route_required"
    )


def test_unvalidated_result_stops():
    record = successful_validation()
    record["validated"] = False

    result = decide(
        validation_result=record
    )

    assert result["decision"] == "STOP"
    assert result["allowed"] is False
    assert result["reason"] == "validated_route_required"


def test_non_simulated_result_stops():
    record = successful_validation()
    record["simulated"] = False

    result = decide(
        validation_result=record
    )

    assert result["decision"] == "STOP"
    assert result["reason"] == "simulated_route_required"


def test_non_test_trade_stops():
    record = successful_validation()
    record["test_trade"] = False

    result = decide(
        validation_result=record
    )

    assert result["decision"] == "STOP"
    assert result["reason"] == "test_trade_required"


def test_live_submission_stops():
    record = successful_validation()
    record["live_order_submitted"] = True

    result = decide(
        validation_result=record
    )

    assert result["decision"] == "STOP"
    assert result["allowed"] is False
    assert result["reason"] == "live_order_already_submitted"
    assert result["live_order_submitted"] is True


def test_current_trade_size_must_be_valid():
    result = decide(
        current_trade_size=1500.0,
        max_trade_size=1000.0,
    )

    assert result["decision"] == "STOP"
    assert result["allowed"] is False
    assert result["reason"] == "current_trade_size_invalid"
    assert result["trade_size_reason"] == "above_maximum"


def test_fresh_controls_are_always_required_for_repeat():
    result = decide(
        successful_test_count=1,
        required_successes_for_scale=2,
    )

    assert result["fresh_revalidation_required"] is True
    assert result["fresh_approval_required"] is True
    assert (
        result["fresh_execution_permission_required"]
        is True
    )


def test_fresh_controls_are_always_required_for_scale():
    result = decide(
        successful_test_count=2,
        required_successes_for_scale=2,
    )

    assert result["fresh_revalidation_required"] is True
    assert result["fresh_approval_required"] is True
    assert (
        result["fresh_execution_permission_required"]
        is True
    )


def test_control_identifiers_are_preserved():
    result = decide()

    assert result["route_id"] == "ROUTE-001"
    assert result["approval_id"] == "ARB-001"
    assert result["permission_id"] == "PERM-001"


def test_profit_details_are_preserved():
    result = decide()

    assert result["net_profit"] == 4.0
    assert result["profit_percent"] == 1.6


def test_missing_validation_result_is_rejected():
    controller = ControlledRepeatScaleDecision()

    with pytest.raises(
        ValueError,
        match="validation_result is required",
    ):
        controller.decide(
            validation_result=None,
            current_trade_size=250.0,
            successful_test_count=1,
            required_successes_for_scale=2,
            scale_multiplier=2.0,
            min_trade_size=10.0,
            max_trade_size=1000.0,
        )


def test_negative_success_count_is_rejected():
    with pytest.raises(
        ValueError,
        match=(
            "successful_test_count must be non-negative"
        ),
    ):
        decide(
            successful_test_count=-1
        )


def test_required_success_count_must_be_positive():
    with pytest.raises(
        ValueError,
        match=(
            "required_successes_for_scale must be positive"
        ),
    ):
        decide(
            required_successes_for_scale=0
        )


def test_scale_multiplier_must_exceed_one():
    with pytest.raises(
        ValueError,
        match=(
            "scale_multiplier must be greater than 1"
        ),
    ):
        decide(
            scale_multiplier=1.0
        )
