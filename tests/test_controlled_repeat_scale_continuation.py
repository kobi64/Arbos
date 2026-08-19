import pytest

from core.controlled_repeat_scale_continuation import (
    ControlledRepeatScaleContinuation,
)
from exchanges.network_registry import NetworkInfo
from core.repeat_scale_market_provenance_binding import (
    RepeatScaleMarketProvenanceBinding,
)


def feedback(
    decision="REPEAT_SAME_SIZE",
    starting_value=250.0,
    next_trade_size=250.0,
    successful_test_count=0,
):
    return {
        "feedback_complete": True,
        "reason": (
            "live_paper_repeat_scale_feedback_complete"
        ),
        "route_id": "ROUTE-001",
        "approval_id": "ARB-002",
        "permission_id": "PERM-002",
        "starting_value": starting_value,
        "final_value": 262.5,
        "validation_result": {
            "validated": True,
            "accepted": True,
            "reason": (
                "simulated_route_validation_passed"
            ),
            "route_id": "ROUTE-001",
            "approval_id": "ARB-002",
            "permission_id": "PERM-002",
            "net_profit": 12.5,
            "profit_percent": 5.0,
            "test_trade": True,
            "simulated": True,
            "paper_trade": True,
            "live_order_submitted": False,
        },
        "decision_result": {
            "decision": decision,
            "allowed": decision != "STOP",
            "reason": (
                "controlled_scale_up_ready"
                if decision == "SCALE_UP"
                else (
                    "additional_successful_test_required"
                    if decision == "REPEAT_SAME_SIZE"
                    else "successful_test_route_required"
                )
            ),
            "route_id": "ROUTE-001",
            "approval_id": "ARB-002",
            "permission_id": "PERM-002",
            "current_trade_size": starting_value,
            "successful_test_count": (
                successful_test_count
            ),
            "required_successes_for_scale": 2,
            "next_trade_size": (
                next_trade_size
            ),
            "fresh_revalidation_required": True,
            "fresh_approval_required": True,
            "fresh_execution_permission_required": True,
            "test_trade": True,
            "simulated": True,
            "live_order_submitted": False,
        },
        "test_trade": True,
        "simulated": True,
        "paper_trade": True,
        "live_order_submitted": False,
    }


def market_provenance_binding():
    provenance = {
        "route_id": "ROUTE-001",
        "independent_revalidation_capture": True,
        "snapshot_age_verified": False,
        "snapshot_count": 2,
        "symbols": [
            "ETH/USDT",
            "ETH/USDT",
        ],
        "exchange_ids": [
            "kucoin",
            "gate",
        ],
        "earliest_timestamp": 1000.0,
        "latest_timestamp": 1000.1,
        "snapshot_spread_ms": 100.0,
        "entry_symbol": "ETH/USDT",
        "entry_side": "buy",
        "available_liquidity": 10000.0,
        "best_price": 100.0,
        "average_price": 99.5,
        "slippage_percent": 0.5,
    }

    return (
        RepeatScaleMarketProvenanceBinding
        .create(provenance)
    )


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


def circuit_allowed():
    return {
        "allowed": True,
        "state": "CLOSED",
        "reason": None,
    }


def portfolio_allowed():
    return {
        "approved": True,
        "reason": None,
        "available_capital": 1000.0,
        "projected_asset_exposure": 0.10,
        "open_routes": 0,
    }


def prepare(
    feedback_result=None,
    repeat_count=0,
    scale_count=0,
    cumulative_trade_amount=250.0,
    max_repeats=5,
    max_scale_steps=2,
    max_cumulative_trade_amount=2000.0,
    circuit=None,
    portfolio=None,
    available_liquidity=10000.0,
    current_price=99.5,
):
    service = (
        ControlledRepeatScaleContinuation()
    )

    record = (
        feedback()
        if feedback_result is None
        else feedback_result
    )

    return service.prepare_next(
        feedback_result=record,
        repeat_count=repeat_count,
        scale_count=scale_count,
        cumulative_trade_amount=(
            cumulative_trade_amount
        ),
        max_repeats=max_repeats,
        max_scale_steps=max_scale_steps,
        max_cumulative_trade_amount=(
            max_cumulative_trade_amount
        ),
        circuit_breaker_result=(
            circuit_allowed()
            if circuit is None
            else circuit
        ),
        portfolio_risk_result=(
            portfolio_allowed()
            if portfolio is None
            else portfolio
        ),
        required_successes_for_scale=2,
        scale_multiplier=2.0,
        min_trade_size=100.0,
        max_trade_size=1000.0,
        source_networks=source_networks(),
        destination_networks=(
            destination_networks()
        ),
        transfer_amount=(
            record.get(
                "starting_value",
                250.0,
            )
        ),
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
        market_provenance_binding=(
            market_provenance_binding()
        ),
    )


def test_same_size_repeat_prepares_next_cycle():
    result = prepare()

    assert result["continuation_ready"] is True
    assert (
        result["stage"]
        == "AWAITING_FRESH_APPROVAL"
    )
    assert result["decision"] == "REPEAT_SAME_SIZE"
    assert result["trade_amount"] == 250.0


def test_scale_decision_prepares_scaled_cycle():
    result = prepare(
        feedback_result=feedback(
            decision="SCALE_UP",
            starting_value=250.0,
            next_trade_size=500.0,
            successful_test_count=2,
        )
    )

    assert result["continuation_ready"] is True
    assert result["decision"] == "SCALE_UP"
    assert result["trade_amount"] == 500.0


def test_repeat_counter_advances():
    result = prepare(
        repeat_count=2
    )

    assert result["repeat_count"] == 2
    assert result["next_repeat_count"] == 3


def test_scale_counter_advances_on_scale():
    result = prepare(
        feedback_result=feedback(
            decision="SCALE_UP",
            next_trade_size=500.0,
            successful_test_count=2,
        ),
        scale_count=1,
    )

    assert result["scale_count"] == 1
    assert result["next_scale_count"] == 2


def test_same_size_repeat_does_not_advance_scale_count():
    result = prepare(
        scale_count=1
    )

    assert result["next_scale_count"] == 1


def test_scale_limit_suppresses_scale_but_allows_repeat():
    result = prepare(
        feedback_result=feedback(
            decision="SCALE_UP",
            next_trade_size=500.0,
            successful_test_count=2,
        ),
        scale_count=2,
        max_scale_steps=2,
    )

    assert result["continuation_ready"] is True
    assert result["scale_suppressed"] is True
    assert result["decision"] == "REPEAT_SAME_SIZE"
    assert result["trade_amount"] == 250.0
    assert result["next_scale_count"] == 2


def test_repeat_limit_hard_stops_cycle():
    result = prepare(
        repeat_count=5,
        max_repeats=5,
    )

    assert result["continuation_ready"] is False
    assert result["hard_stop"] is True
    assert result["stage"] == "LIMITS"
    assert (
        result["reason"]
        == "maximum_repeat_count_reached"
    )


def test_cumulative_limit_hard_stops_cycle():
    result = prepare(
        cumulative_trade_amount=1900.0,
        max_cumulative_trade_amount=2000.0,
    )

    assert result["continuation_ready"] is False
    assert result["hard_stop"] is True
    assert (
        result["reason"]
        == "maximum_cumulative_trade_amount_exceeded"
    )


def test_open_circuit_hard_stops_cycle():
    result = prepare(
        circuit={
            "allowed": False,
            "state": "OPEN",
            "reason": "circuit_open",
        }
    )

    assert result["continuation_ready"] is False
    assert result["hard_stop"] is True
    assert result["reason"] == "execution_circuit_open"


def test_portfolio_rejection_hard_stops_cycle():
    result = prepare(
        portfolio={
            "approved": False,
            "reason": "asset_exposure_exceeded",
        }
    )

    assert result["continuation_ready"] is False
    assert result["hard_stop"] is True
    assert result["reason"] == "asset_exposure_exceeded"


def test_feedback_stop_decision_stops_immediately():
    result = prepare(
        feedback_result=feedback(
            decision="STOP"
        )
    )

    assert result["continuation_ready"] is False
    assert result["hard_stop"] is True
    assert result["stage"] == "DECISION"


def test_incomplete_feedback_is_blocked():
    record = feedback()
    record["feedback_complete"] = False

    result = prepare(
        feedback_result=record
    )

    assert result["continuation_ready"] is False
    assert result["stage"] == "FEEDBACK"
    assert (
        result["reason"]
        == "completed_feedback_required"
    )


def test_live_feedback_is_blocked():
    record = feedback()
    record["live_order_submitted"] = True

    result = prepare(
        feedback_result=record
    )

    assert result["continuation_ready"] is False
    assert result["hard_stop"] is True
    assert (
        result["reason"]
        == "live_order_already_submitted"
    )
    assert result["live_order_submitted"] is True


def test_missing_feedback_decision_is_blocked():
    record = feedback()
    record.pop("decision_result")

    result = prepare(
        feedback_result=record
    )

    assert result["continuation_ready"] is False
    assert result["reason"] == "feedback_decision_required"


def test_missing_validation_result_is_blocked():
    record = feedback()
    record.pop("validation_result")

    result = prepare(
        feedback_result=record
    )

    assert result["continuation_ready"] is False
    assert result["reason"] == "validation_result_required"


def test_liquidity_failure_blocks_next_cycle():
    result = prepare(
        available_liquidity=1000.0
    )

    assert result["continuation_ready"] is False
    assert result["hard_stop"] is False
    assert result["stage"] == "NEXT_CYCLE"
    assert (
        result["reason"]
        == "liquidity_revalidation_failed"
    )


def test_slippage_failure_blocks_next_cycle():
    result = prepare(
        current_price=98.0
    )

    assert result["continuation_ready"] is False
    assert result["hard_stop"] is False
    assert result["stage"] == "NEXT_CYCLE"
    assert (
        result["reason"]
        == "slippage_revalidation_failed"
    )


def test_next_cycle_still_requires_manual_approval():
    result = prepare()

    assert (
        result["manual_approval_required"]
        is True
    )
    assert result["approval_granted"] is False


def test_next_cycle_still_requires_fresh_permission():
    result = prepare()

    assert (
        result[
            "fresh_execution_permission_required"
        ]
        is True
    )
    assert result["permission_granted"] is False


def test_next_cycle_contains_fresh_revalidation_result():
    result = prepare()

    next_cycle = result["next_cycle"]

    assert (
        next_cycle[
            "revalidation_result"
        ]["revalidated"]
        is True
    )


def test_projected_cumulative_amount_is_preserved():
    result = prepare(
        cumulative_trade_amount=500.0
    )

    assert (
        result[
            "projected_cumulative_trade_amount"
        ]
        == 750.0
    )


def test_missing_feedback_is_rejected():
    service = (
        ControlledRepeatScaleContinuation()
    )

    with pytest.raises(
        ValueError,
        match="feedback_result is required",
    ):
        service.prepare_next(
            feedback_result=None,
            repeat_count=0,
            scale_count=0,
            cumulative_trade_amount=0.0,
            max_repeats=5,
            max_scale_steps=2,
            max_cumulative_trade_amount=2000.0,
            circuit_breaker_result=circuit_allowed(),
            portfolio_risk_result=portfolio_allowed(),
            required_successes_for_scale=2,
            scale_multiplier=2.0,
            min_trade_size=100.0,
            max_trade_size=1000.0,
            source_networks=source_networks(),
            destination_networks=destination_networks(),
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


def test_continuation_is_recorded_in_history():
    service = (
        ControlledRepeatScaleContinuation()
    )

    record = feedback()

    service.prepare_next(
        feedback_result=record,
        repeat_count=0,
        scale_count=0,
        cumulative_trade_amount=250.0,
        max_repeats=5,
        max_scale_steps=2,
        max_cumulative_trade_amount=2000.0,
        circuit_breaker_result=circuit_allowed(),
        portfolio_risk_result=portfolio_allowed(),
        required_successes_for_scale=2,
        scale_multiplier=2.0,
        min_trade_size=100.0,
        max_trade_size=1000.0,
        source_networks=source_networks(),
        destination_networks=destination_networks(),
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

    assert len(service.history()) == 1


def test_entire_continuation_remains_paper_only():
    result = prepare()

    assert result["test_trade"] is True
    assert result["simulated"] is True
    assert result["paper_trade"] is True
    assert result["live_order_submitted"] is False

    assert (
        result["next_cycle"][
            "live_order_submitted"
        ]
        is False
    )
