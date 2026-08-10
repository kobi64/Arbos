import pytest

from core.repeat_scale_cycle_integration import (
    RepeatScaleCycleIntegration,
)
from core.staged_test_trade_execution_permission import (
    StagedTestTradeExecutionPermission,
)
from exchanges.network_registry import NetworkInfo


def validation_result():
    return {
        "validated": True,
        "accepted": True,
        "reason": "simulated_route_validated",
        "route_id": "ROUTE-001",
        "approval_id": "ARB-001",
        "permission_id": "PERM-001",
        "net_profit": 5.0,
        "profit_percent": 2.0,
        "test_trade": True,
        "simulated": True,
        "live_order_submitted": False,
    }


def source_networks():
    return [
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_fee=1.0,
            min_withdraw=10.0,
        ),
    ]


def destination_networks():
    return [
        NetworkInfo(
            "USDT",
            "TRC20",
        ),
    ]


def prepare_cycle(
    validation=None,
    current_trade_size=250.0,
    successful_test_count=0,
    required_successes_for_scale=2,
    scale_multiplier=2.0,
    max_trade_size=1000.0,
    available_liquidity=10000.0,
    current_price=99.5,
):
    coordinator = RepeatScaleCycleIntegration()

    return coordinator.prepare_approval(
        validation_result=(
            validation_result()
            if validation is None
            else validation
        ),
        current_trade_size=current_trade_size,
        successful_test_count=(
            successful_test_count
        ),
        required_successes_for_scale=(
            required_successes_for_scale
        ),
        scale_multiplier=scale_multiplier,
        min_trade_size=100.0,
        max_trade_size=max_trade_size,
        source_networks=source_networks(),
        destination_networks=(
            destination_networks()
        ),
        transfer_amount=current_trade_size,
        available_liquidity=(
            available_liquidity
        ),
        minimum_liquidity_ratio=0.1,
        expected_price=100.0,
        current_price=current_price,
        max_slippage_percent=1.0,
        asset="ETH",
        buy_exchange="kucoin",
        sell_exchange="gate",
        expected_profit=5.0,
        estimated_fees=0.5,
        slippage_allowance=0.25,
    )


def fresh_approval(
    trade_amount=250.0,
    approval_id="ARB-002",
):
    return {
        "approval_id": approval_id,
        "route_id": "ROUTE-001",
        "approved": True,
        "status": "approved",
        "trade_summary": {
            "asset": "ETH",
            "trade_amount": trade_amount,
            "route": "kucoin -> gate",
            "expected_profit": 5.0,
        },
        "live_order_submitted": False,
    }


def test_repeat_cycle_reaches_fresh_approval_boundary():
    result = prepare_cycle()

    assert result["cycle_ready"] is True
    assert (
        result["stage"]
        == "AWAITING_FRESH_APPROVAL"
    )
    assert result["decision"] == "REPEAT_SAME_SIZE"
    assert result["trade_amount"] == 250.0


def test_scale_cycle_reaches_fresh_approval_boundary():
    result = prepare_cycle(
        successful_test_count=2
    )

    assert result["cycle_ready"] is True
    assert result["decision"] == "SCALE_UP"
    assert result["trade_amount"] == 500.0


def test_cycle_preserves_all_intermediate_results():
    result = prepare_cycle()

    assert "decision_result" in result
    assert "revalidation_result" in result
    assert "approval_handoff" in result

    assert (
        result["decision_result"]["allowed"]
        is True
    )
    assert (
        result["revalidation_result"]["revalidated"]
        is True
    )
    assert (
        result["approval_handoff"]["approval_ready"]
        is True
    )


def test_old_control_ids_remain_audit_lineage():
    result = prepare_cycle()

    handoff = result["approval_handoff"]

    assert handoff["previous_approval_id"] == "ARB-001"
    assert handoff["previous_permission_id"] == "PERM-001"
    assert handoff["approval_granted"] is False
    assert handoff["permission_granted"] is False


def test_manual_approval_boundary_is_preserved():
    result = prepare_cycle()

    assert result["manual_approval_required"] is True
    assert result["approval_granted"] is False
    assert result["permission_granted"] is False


def test_failed_route_validation_stops_at_decision():
    validation = validation_result()
    validation["validated"] = False

    result = prepare_cycle(
        validation=validation
    )

    assert result["cycle_ready"] is False
    assert result["stage"] == "DECISION"
    assert result["reason"] == "validated_route_required"


def test_unsuccessful_route_stops_at_decision():
    validation = validation_result()
    validation["accepted"] = False

    result = prepare_cycle(
        validation=validation
    )

    assert result["cycle_ready"] is False
    assert result["stage"] == "DECISION"
    assert (
        result["reason"]
        == "successful_test_route_required"
    )


def test_liquidity_failure_stops_at_revalidation():
    result = prepare_cycle(
        available_liquidity=1000.0
    )

    assert result["cycle_ready"] is False
    assert result["stage"] == "REVALIDATION"
    assert (
        result["reason"]
        == "liquidity_revalidation_failed"
    )


def test_slippage_failure_stops_at_revalidation():
    result = prepare_cycle(
        current_price=98.0
    )

    assert result["cycle_ready"] is False
    assert result["stage"] == "REVALIDATION"
    assert (
        result["reason"]
        == "slippage_revalidation_failed"
    )


def test_scale_uses_scaled_size_for_liquidity_gate():
    result = prepare_cycle(
        successful_test_count=2,
        available_liquidity=4000.0,
    )

    assert result["cycle_ready"] is False
    assert result["stage"] == "REVALIDATION"
    assert (
        result["reason"]
        == "liquidity_revalidation_failed"
    )


def test_scale_limit_falls_back_to_same_size():
    result = prepare_cycle(
        successful_test_count=2,
        max_trade_size=400.0,
    )

    assert result["cycle_ready"] is True
    assert result["decision"] == "REPEAT_SAME_SIZE"
    assert result["trade_amount"] == 250.0
    assert (
        result["decision_result"]["reason"]
        == "scale_limit_reached"
    )


def test_fresh_approval_can_progress_to_permission_handoff():
    coordinator = RepeatScaleCycleIntegration()

    cycle = prepare_cycle()

    result = coordinator.prepare_permission(
        cycle_result=cycle,
        approval_result=fresh_approval(),
    )

    assert result["cycle_ready"] is True
    assert result["permission_handoff_ready"] is True
    assert (
        result["stage"]
        == "AWAITING_EXECUTION_PERMISSION"
    )
    assert result["approval_id"] == "ARB-002"


def test_scaled_fresh_approval_uses_scaled_amount():
    coordinator = RepeatScaleCycleIntegration()

    cycle = prepare_cycle(
        successful_test_count=2
    )

    result = coordinator.prepare_permission(
        cycle_result=cycle,
        approval_result=fresh_approval(
            trade_amount=500.0
        ),
    )

    assert result["permission_handoff_ready"] is True
    assert result["decision"] == "SCALE_UP"
    assert result["trade_amount"] == 500.0


def test_wrong_fresh_approval_amount_is_blocked():
    coordinator = RepeatScaleCycleIntegration()

    cycle = prepare_cycle(
        successful_test_count=2
    )

    result = coordinator.prepare_permission(
        cycle_result=cycle,
        approval_result=fresh_approval(
            trade_amount=250.0
        ),
    )

    assert result["cycle_ready"] is False
    assert result["stage"] == "PERMISSION_HANDOFF"
    assert (
        result["reason"]
        == "approved_trade_amount_mismatch"
    )


def test_previous_approval_cannot_authorize_new_cycle():
    coordinator = RepeatScaleCycleIntegration()

    cycle = prepare_cycle()

    result = coordinator.prepare_permission(
        cycle_result=cycle,
        approval_result=fresh_approval(
            approval_id="ARB-001"
        ),
    )

    assert result["cycle_ready"] is False
    assert (
        result["reason"]
        == "previous_approval_id_reuse_blocked"
    )


def test_permission_handoff_can_feed_single_use_gate():
    coordinator = RepeatScaleCycleIntegration()

    cycle = prepare_cycle()

    result = coordinator.prepare_permission(
        cycle_result=cycle,
        approval_result=fresh_approval(),
    )

    permission_gate = (
        StagedTestTradeExecutionPermission()
    )

    permission = permission_gate.create(
        handoff_result=(
            result["permission_handoff"]
        )
    )

    assert permission["permission_granted"] is False
    assert (
        permission["status"]
        == "awaiting_execution_permission"
    )
    assert permission["trade_amount"] == 250.0


def test_scaled_permission_rejects_old_amount():
    coordinator = RepeatScaleCycleIntegration()

    cycle = prepare_cycle(
        successful_test_count=2
    )

    result = coordinator.prepare_permission(
        cycle_result=cycle,
        approval_result=fresh_approval(
            trade_amount=500.0
        ),
    )

    permission_gate = (
        StagedTestTradeExecutionPermission()
    )

    permission = permission_gate.create(
        handoff_result=(
            result["permission_handoff"]
        )
    )

    granted = permission_gate.grant(
        permission_id=permission["permission_id"],
        trade_amount=250.0,
    )

    assert granted["permission_granted"] is False
    assert granted["reason"] == "trade_amount_mismatch"


def test_scaled_permission_accepts_exact_new_amount():
    coordinator = RepeatScaleCycleIntegration()

    cycle = prepare_cycle(
        successful_test_count=2
    )

    result = coordinator.prepare_permission(
        cycle_result=cycle,
        approval_result=fresh_approval(
            trade_amount=500.0
        ),
    )

    permission_gate = (
        StagedTestTradeExecutionPermission()
    )

    permission = permission_gate.create(
        handoff_result=(
            result["permission_handoff"]
        )
    )

    granted = permission_gate.grant(
        permission_id=permission["permission_id"],
        trade_amount=500.0,
    )

    assert granted["permission_granted"] is True
    assert granted["trade_amount"] == 500.0


def test_permission_remains_single_use_end_to_end():
    coordinator = RepeatScaleCycleIntegration()

    cycle = prepare_cycle()

    result = coordinator.prepare_permission(
        cycle_result=cycle,
        approval_result=fresh_approval(),
    )

    permission_gate = (
        StagedTestTradeExecutionPermission()
    )

    permission = permission_gate.create(
        handoff_result=(
            result["permission_handoff"]
        )
    )

    first = permission_gate.grant(
        permission_id=permission["permission_id"],
        trade_amount=250.0,
    )

    second = permission_gate.grant(
        permission_id=permission["permission_id"],
        trade_amount=250.0,
    )

    assert first["permission_granted"] is True
    assert second["permission_granted"] is False
    assert second["status"] == "not_found"


def test_unprepared_cycle_cannot_prepare_permission():
    coordinator = RepeatScaleCycleIntegration()

    result = coordinator.prepare_permission(
        cycle_result={
            "cycle_ready": False,
            "stage": "DECISION",
            "live_order_submitted": False,
        },
        approval_result=fresh_approval(),
    )

    assert result["permission_handoff_ready"] is False
    assert result["reason"] == "prepared_cycle_required"


def test_wrong_cycle_stage_cannot_prepare_permission():
    coordinator = RepeatScaleCycleIntegration()

    cycle = prepare_cycle()
    cycle["stage"] = "OTHER"

    result = coordinator.prepare_permission(
        cycle_result=cycle,
        approval_result=fresh_approval(),
    )

    assert result["permission_handoff_ready"] is False
    assert (
        result["reason"]
        == "fresh_approval_stage_required"
    )


def test_live_submission_is_blocked_between_stages():
    coordinator = RepeatScaleCycleIntegration()

    cycle = prepare_cycle()
    cycle["live_order_submitted"] = True

    result = coordinator.prepare_permission(
        cycle_result=cycle,
        approval_result=fresh_approval(),
    )

    assert result["permission_handoff_ready"] is False
    assert result["reason"] == "live_order_already_submitted"
    assert result["live_order_submitted"] is True


def test_missing_validation_result_is_rejected():
    coordinator = RepeatScaleCycleIntegration()

    with pytest.raises(
        ValueError,
        match="validation_result is required",
    ):
        coordinator.prepare_approval(
            validation_result=None,
            current_trade_size=250.0,
            successful_test_count=0,
            required_successes_for_scale=2,
            scale_multiplier=2.0,
            min_trade_size=100.0,
            max_trade_size=1000.0,
            source_networks=source_networks(),
            destination_networks=(
                destination_networks()
            ),
            transfer_amount=250.0,
            available_liquidity=10000.0,
            minimum_liquidity_ratio=0.1,
            expected_price=100.0,
            current_price=99.5,
            max_slippage_percent=1.0,
            asset="ETH",
            buy_exchange="kucoin",
            sell_exchange="gate",
            expected_profit=5.0,
            estimated_fees=0.5,
            slippage_allowance=0.25,
        )


def test_missing_cycle_result_is_rejected():
    coordinator = RepeatScaleCycleIntegration()

    with pytest.raises(
        ValueError,
        match="cycle_result is required",
    ):
        coordinator.prepare_permission(
            cycle_result=None,
            approval_result=fresh_approval(),
        )


def test_missing_approval_result_is_rejected():
    coordinator = RepeatScaleCycleIntegration()

    with pytest.raises(
        ValueError,
        match="approval_result is required",
    ):
        coordinator.prepare_permission(
            cycle_result=prepare_cycle(),
            approval_result=None,
        )


def test_integration_never_submits_live_order():
    coordinator = RepeatScaleCycleIntegration()

    cycle = prepare_cycle()

    permission = coordinator.prepare_permission(
        cycle_result=cycle,
        approval_result=fresh_approval(),
    )

    assert cycle["live_order_submitted"] is False
    assert permission["live_order_submitted"] is False
    assert cycle["simulated"] is True
    assert permission["simulated"] is True
