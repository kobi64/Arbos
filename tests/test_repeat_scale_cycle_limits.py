import pytest

from core.execution_circuit_breaker import (
    ExecutionCircuitBreaker,
)
from core.repeat_scale_cycle_limits import (
    RepeatScaleCycleLimits,
)
from exchanges.portfolio_exposure_concurrent_risk import (
    PortfolioExposureConcurrentRisk,
)


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


def evaluate(
    repeat_count=0,
    scale_count=0,
    cumulative_trade_amount=0.0,
    next_trade_amount=250.0,
    max_repeats=5,
    max_scale_steps=2,
    max_cumulative_trade_amount=2000.0,
    circuit=None,
    portfolio=None,
):
    return RepeatScaleCycleLimits().evaluate(
        repeat_count=repeat_count,
        scale_count=scale_count,
        cumulative_trade_amount=(
            cumulative_trade_amount
        ),
        next_trade_amount=next_trade_amount,
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
    )


def test_safe_cycle_is_allowed():
    result = evaluate()

    assert result["allowed"] is True
    assert result["hard_stop"] is False
    assert result["reason"] is None


def test_allowed_cycle_increments_repeat_counter():
    result = evaluate(
        repeat_count=2
    )

    assert result["repeat_count"] == 2
    assert result["next_repeat_count"] == 3


def test_projected_cumulative_amount_is_calculated():
    result = evaluate(
        cumulative_trade_amount=500.0,
        next_trade_amount=250.0,
    )

    assert (
        result["projected_cumulative_trade_amount"]
        == 750.0
    )


def test_repeat_limit_is_hard_stop():
    result = evaluate(
        repeat_count=5,
        max_repeats=5,
    )

    assert result["allowed"] is False
    assert result["hard_stop"] is True
    assert (
        result["reason"]
        == "maximum_repeat_count_reached"
    )


def test_repeat_below_limit_is_allowed():
    result = evaluate(
        repeat_count=4,
        max_repeats=5,
    )

    assert result["allowed"] is True
    assert result["next_repeat_count"] == 5


def test_zero_repeat_limit_blocks_first_repeat():
    result = evaluate(
        repeat_count=0,
        max_repeats=0,
    )

    assert result["allowed"] is False
    assert (
        result["reason"]
        == "maximum_repeat_count_reached"
    )


def test_scale_limit_does_not_block_same_size_repeat():
    result = evaluate(
        scale_count=2,
        max_scale_steps=2,
    )

    assert result["allowed"] is True
    assert result["scale_allowed"] is False


def test_scale_below_limit_remains_allowed():
    result = evaluate(
        scale_count=1,
        max_scale_steps=2,
    )

    assert result["allowed"] is True
    assert result["scale_allowed"] is True


def test_scale_evaluation_blocks_when_limit_reached():
    limits = RepeatScaleCycleLimits()

    result = evaluate(
        scale_count=2,
        max_scale_steps=2,
    )

    scale = limits.evaluate_scale(
        limit_result=result
    )

    assert scale["scale_allowed"] is False
    assert (
        scale["reason"]
        == "maximum_scale_steps_reached"
    )


def test_scale_evaluation_allows_safe_scale():
    limits = RepeatScaleCycleLimits()

    result = evaluate(
        scale_count=1,
        max_scale_steps=2,
    )

    scale = limits.evaluate_scale(
        limit_result=result
    )

    assert scale["scale_allowed"] is True
    assert scale["reason"] is None


def test_cumulative_limit_is_hard_stop():
    result = evaluate(
        cumulative_trade_amount=1900.0,
        next_trade_amount=250.0,
        max_cumulative_trade_amount=2000.0,
    )

    assert result["allowed"] is False
    assert result["hard_stop"] is True
    assert (
        result["reason"]
        == "maximum_cumulative_trade_amount_exceeded"
    )


def test_exact_cumulative_limit_is_allowed():
    result = evaluate(
        cumulative_trade_amount=1750.0,
        next_trade_amount=250.0,
        max_cumulative_trade_amount=2000.0,
    )

    assert result["allowed"] is True
    assert (
        result["projected_cumulative_trade_amount"]
        == 2000.0
    )


def test_open_circuit_is_hard_stop():
    result = evaluate(
        circuit={
            "allowed": False,
            "state": "OPEN",
            "reason": "circuit_open",
        }
    )

    assert result["allowed"] is False
    assert result["hard_stop"] is True
    assert result["reason"] == "execution_circuit_open"


def test_portfolio_capital_rejection_is_hard_stop():
    result = evaluate(
        portfolio={
            "approved": False,
            "reason": "insufficient_unreserved_capital",
        }
    )

    assert result["allowed"] is False
    assert (
        result["reason"]
        == "insufficient_unreserved_capital"
    )


def test_asset_exposure_rejection_is_hard_stop():
    result = evaluate(
        portfolio={
            "approved": False,
            "reason": "asset_exposure_exceeded",
        }
    )

    assert result["allowed"] is False
    assert result["reason"] == "asset_exposure_exceeded"


def test_concurrent_route_rejection_is_hard_stop():
    result = evaluate(
        portfolio={
            "approved": False,
            "reason": "concurrent_route_limit_reached",
        }
    )

    assert result["allowed"] is False
    assert (
        result["reason"]
        == "concurrent_route_limit_reached"
    )


def test_real_circuit_breaker_open_result_is_respected():
    breaker = ExecutionCircuitBreaker(
        failure_threshold=2,
        recovery_timeout_seconds=30,
    )

    breaker.record_failure("one")
    breaker.record_failure("two")

    circuit = breaker.allow_execution()

    result = evaluate(
        circuit=circuit
    )

    assert circuit["state"] == "OPEN"
    assert result["allowed"] is False
    assert result["reason"] == "execution_circuit_open"


def test_real_portfolio_risk_rejection_is_respected():
    engine = PortfolioExposureConcurrentRisk()

    portfolio = {
        "total_capital": 1000.0,
        "reserved_capital": 900.0,
        "asset_exposure": {
            "ETH": 0.05,
        },
        "max_asset_exposure": 0.25,
        "open_routes": 0,
    }

    risk = engine.evaluate(
        portfolio=portfolio,
        asset="ETH",
        additional_exposure=0.01,
        required_capital=250.0,
    )

    result = evaluate(
        portfolio=risk
    )

    assert risk["approved"] is False
    assert result["allowed"] is False
    assert (
        result["reason"]
        == "insufficient_unreserved_capital"
    )


def test_negative_repeat_count_is_rejected():
    with pytest.raises(
        ValueError,
        match="repeat_count cannot be negative",
    ):
        evaluate(
            repeat_count=-1
        )


def test_negative_scale_count_is_rejected():
    with pytest.raises(
        ValueError,
        match="scale_count cannot be negative",
    ):
        evaluate(
            scale_count=-1
        )


def test_negative_cumulative_amount_is_rejected():
    with pytest.raises(
        ValueError,
        match=(
            "cumulative_trade_amount cannot be negative"
        ),
    ):
        evaluate(
            cumulative_trade_amount=-1.0
        )


def test_non_positive_next_trade_amount_is_rejected():
    with pytest.raises(
        ValueError,
        match="next_trade_amount must be positive",
    ):
        evaluate(
            next_trade_amount=0.0
        )


def test_negative_max_repeats_is_rejected():
    with pytest.raises(
        ValueError,
        match="max_repeats cannot be negative",
    ):
        evaluate(
            max_repeats=-1
        )


def test_negative_max_scale_steps_is_rejected():
    with pytest.raises(
        ValueError,
        match="max_scale_steps cannot be negative",
    ):
        evaluate(
            max_scale_steps=-1
        )


def test_non_positive_cumulative_limit_is_rejected():
    with pytest.raises(
        ValueError,
        match=(
            "max_cumulative_trade_amount must be positive"
        ),
    ):
        evaluate(
            max_cumulative_trade_amount=0.0
        )


def test_missing_circuit_result_is_rejected():
    limits = RepeatScaleCycleLimits()

    with pytest.raises(
        ValueError,
        match="circuit_breaker_result is required",
    ):
        limits.evaluate(
            repeat_count=0,
            scale_count=0,
            cumulative_trade_amount=0.0,
            next_trade_amount=250.0,
            max_repeats=5,
            max_scale_steps=2,
            max_cumulative_trade_amount=2000.0,
            circuit_breaker_result=None,
            portfolio_risk_result=portfolio_allowed(),
        )


def test_missing_portfolio_result_is_rejected():
    limits = RepeatScaleCycleLimits()

    with pytest.raises(
        ValueError,
        match="portfolio_risk_result is required",
    ):
        limits.evaluate(
            repeat_count=0,
            scale_count=0,
            cumulative_trade_amount=0.0,
            next_trade_amount=250.0,
            max_repeats=5,
            max_scale_steps=2,
            max_cumulative_trade_amount=2000.0,
            circuit_breaker_result=circuit_allowed(),
            portfolio_risk_result=None,
        )


def test_scale_evaluation_requires_limit_result():
    limits = RepeatScaleCycleLimits()

    with pytest.raises(
        ValueError,
        match="limit_result is required",
    ):
        limits.evaluate_scale(
            limit_result=None
        )


def test_blocked_cycle_cannot_scale():
    limits = RepeatScaleCycleLimits()

    result = evaluate(
        repeat_count=5,
        max_repeats=5,
    )

    scale = limits.evaluate_scale(
        limit_result=result
    )

    assert scale["scale_allowed"] is False
    assert scale["reason"] == "cycle_not_allowed"


def test_limit_engine_never_submits_live_order():
    result = evaluate()

    assert result["live_order_submitted"] is False
