import pytest

from exchanges.liquidity_validation import LiquidityValidation


def test_accepts_trade_with_sufficient_liquidity():
    result = LiquidityValidation.validate(
        trade_size=1000.0,
        available_liquidity=10000.0,
        minimum_liquidity_ratio=0.1,
    )

    assert result["valid"] is True
    assert result["reason"] is None


def test_rejects_trade_when_liquidity_is_too_low():
    result = LiquidityValidation.validate(
        trade_size=5000.0,
        available_liquidity=1000.0,
        minimum_liquidity_ratio=0.1,
    )

    assert result["valid"] is False
    assert result["reason"] == "insufficient_liquidity"


def test_accepts_exact_liquidity_requirement():
    result = LiquidityValidation.validate(
        trade_size=1000.0,
        available_liquidity=10000.0,
        minimum_liquidity_ratio=0.1,
    )

    assert result["valid"] is True


def test_rejects_zero_trade_size():
    result = LiquidityValidation.validate(
        trade_size=0.0,
        available_liquidity=10000.0,
        minimum_liquidity_ratio=0.1,
    )

    assert result["valid"] is False
    assert result["reason"] == "non_positive_trade_size"


def test_rejects_negative_trade_size():
    result = LiquidityValidation.validate(
        trade_size=-100.0,
        available_liquidity=10000.0,
        minimum_liquidity_ratio=0.1,
    )

    assert result["valid"] is False
    assert result["reason"] == "non_positive_trade_size"


def test_rejects_zero_liquidity():
    result = LiquidityValidation.validate(
        trade_size=1000.0,
        available_liquidity=0.0,
        minimum_liquidity_ratio=0.1,
    )

    assert result["valid"] is False
    assert result["reason"] == "insufficient_liquidity"


def test_rejects_invalid_liquidity_ratio():
    with pytest.raises(ValueError):
        LiquidityValidation.validate(
            trade_size=1000.0,
            available_liquidity=10000.0,
            minimum_liquidity_ratio=-0.1,
        )


def test_rejects_trade_size_larger_than_available_liquidity():
    result = LiquidityValidation.validate(
        trade_size=20000.0,
        available_liquidity=10000.0,
        minimum_liquidity_ratio=0.1,
    )

    assert result["valid"] is False
    assert result["reason"] == "insufficient_liquidity"
