import pytest

from exchanges.slippage_validation import SlippageValidation


def test_accepts_slippage_within_limit():
    result = SlippageValidation.validate(
        expected_price=100.0,
        execution_price=99.5,
        max_slippage_percent=1.0,
    )

    assert result["valid"] is True
    assert result["reason"] is None


def test_accepts_zero_slippage():
    result = SlippageValidation.validate(
        expected_price=100.0,
        execution_price=100.0,
        max_slippage_percent=0.0,
    )

    assert result["valid"] is True


def test_rejects_slippage_above_limit():
    result = SlippageValidation.validate(
        expected_price=100.0,
        execution_price=98.0,
        max_slippage_percent=1.0,
    )

    assert result["valid"] is False
    assert result["reason"] == "slippage_exceeded"


def test_accepts_exact_maximum_slippage():
    result = SlippageValidation.validate(
        expected_price=100.0,
        execution_price=99.0,
        max_slippage_percent=1.0,
    )

    assert result["valid"] is True


def test_rejects_negative_max_slippage_limit():
    with pytest.raises(ValueError):
        SlippageValidation.validate(
            expected_price=100.0,
            execution_price=99.0,
            max_slippage_percent=-1.0,
        )


def test_rejects_zero_expected_price():
    with pytest.raises(ValueError):
        SlippageValidation.validate(
            expected_price=0.0,
            execution_price=99.0,
            max_slippage_percent=1.0,
        )


def test_handles_price_improvement():
    result = SlippageValidation.validate(
        expected_price=100.0,
        execution_price=101.0,
        max_slippage_percent=1.0,
    )

    assert result["valid"] is True


def test_does_not_modify_inputs():
    expected_price = 100.0
    execution_price = 99.5
    max_slippage = 1.0

    SlippageValidation.validate(
        expected_price,
        execution_price,
        max_slippage,
    )

    assert expected_price == 100.0
    assert execution_price == 99.5
    assert max_slippage == 1.0
