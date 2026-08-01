import pytest

from exchanges.trade_size_validation import TradeSizeValidation


def test_accepts_trade_size_within_limits():
    result = TradeSizeValidation.validate(
        trade_size=500.0,
        min_trade_size=100.0,
        max_trade_size=1000.0,
    )

    assert result["valid"] is True
    assert result["reason"] is None


def test_accepts_trade_size_at_minimum():
    result = TradeSizeValidation.validate(
        trade_size=100.0,
        min_trade_size=100.0,
        max_trade_size=1000.0,
    )

    assert result["valid"] is True


def test_accepts_trade_size_at_maximum():
    result = TradeSizeValidation.validate(
        trade_size=1000.0,
        min_trade_size=100.0,
        max_trade_size=1000.0,
    )

    assert result["valid"] is True


def test_rejects_trade_size_below_minimum():
    result = TradeSizeValidation.validate(
        trade_size=99.99,
        min_trade_size=100.0,
        max_trade_size=1000.0,
    )

    assert result["valid"] is False
    assert result["reason"] == "below_minimum"


def test_rejects_trade_size_above_maximum():
    result = TradeSizeValidation.validate(
        trade_size=1000.01,
        min_trade_size=100.0,
        max_trade_size=1000.0,
    )

    assert result["valid"] is False
    assert result["reason"] == "above_maximum"


def test_rejects_zero_trade_size():
    result = TradeSizeValidation.validate(
        trade_size=0.0,
        min_trade_size=0.0,
        max_trade_size=1000.0,
    )

    assert result["valid"] is False
    assert result["reason"] == "non_positive_trade_size"


def test_rejects_negative_trade_size():
    result = TradeSizeValidation.validate(
        trade_size=-100.0,
        min_trade_size=100.0,
        max_trade_size=1000.0,
    )

    assert result["valid"] is False
    assert result["reason"] == "non_positive_trade_size"


def test_rejects_invalid_limits():
    with pytest.raises(ValueError):
        TradeSizeValidation.validate(
            trade_size=500.0,
            min_trade_size=1000.0,
            max_trade_size=100.0,
        )
