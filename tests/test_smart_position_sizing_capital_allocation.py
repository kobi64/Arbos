import pytest

from exchanges.smart_position_sizing_capital_allocation import (
    SmartPositionSizingCapitalAllocation,
)


@pytest.fixture
def engine():
    return SmartPositionSizingCapitalAllocation()


def sample_inputs():
    return {
        "available_balance": 1000.0,
        "risk_maximum_trade": 250.0,
        "user_trade_cap": 300.0,
        "liquidity_trade_cap": 220.0,
        "min_trade_size": 10.0,
        "quantity_step": 0.01,
    }


def test_selects_smallest_safe_trade_cap(engine):
    result = engine.calculate(**sample_inputs())

    assert result["recommended_trade_size"] == 220.0
    assert result["limiting_factor"] == "liquidity_trade_cap"


def test_available_balance_can_limit_trade_size(engine):
    inputs = sample_inputs()
    inputs["available_balance"] = 150.0

    result = engine.calculate(**inputs)

    assert result["recommended_trade_size"] == 150.0
    assert result["limiting_factor"] == "available_balance"


def test_rounds_down_to_quantity_step(engine):
    inputs = sample_inputs()
    inputs["liquidity_trade_cap"] = 220.007

    result = engine.calculate(**inputs)

    assert result["recommended_trade_size"] == 220.0


def test_rejects_size_below_minimum(engine):
    inputs = sample_inputs()
    inputs["available_balance"] = 5.0

    result = engine.calculate(**inputs)

    assert result["valid"] is False
    assert result["reason"] == "below_minimum_trade_size"


def test_rejects_non_positive_available_balance(engine):
    inputs = sample_inputs()
    inputs["available_balance"] = 0.0

    with pytest.raises(ValueError, match="available_balance must be positive"):
        engine.calculate(**inputs)


def test_rejects_non_positive_quantity_step(engine):
    inputs = sample_inputs()
    inputs["quantity_step"] = 0.0

    with pytest.raises(ValueError, match="quantity_step must be positive"):
        engine.calculate(**inputs)
