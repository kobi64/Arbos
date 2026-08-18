import pytest
from exchanges.trade_cost_analysis import TradeCostAnalysis


def test_calculates_single_trade_fee():
    result = TradeCostAnalysis.evaluate(
        trade_value=1000.0,
        fee_percent=0.1,
    )

    assert result.valid is True
    assert result.fee_amount == 1.0
    assert result.net_value == 999.0
    assert result.reason == "ok"


def test_rejects_zero_trade_value():
    result = TradeCostAnalysis.evaluate(
        trade_value=0.0,
        fee_percent=0.1,
    )

    assert result.valid is False
    assert result.reason == "invalid_trade_value"


def test_rejects_negative_trade_value():
    result = TradeCostAnalysis.evaluate(
        trade_value=-100.0,
        fee_percent=0.1,
    )

    assert result.valid is False
    assert result.reason == "invalid_trade_value"


def test_rejects_negative_fee_percent():
    result = TradeCostAnalysis.evaluate(
        trade_value=1000.0,
        fee_percent=-0.1,
    )

    assert result.valid is False
    assert result.reason == "invalid_fee_percent"


def test_accepts_zero_fee():
    result = TradeCostAnalysis.evaluate(
        trade_value=1000.0,
        fee_percent=0.0,
    )

    assert result.valid is True
    assert result.fee_amount == 0.0
    assert result.net_value == 1000.0


def test_rejects_fee_that_consumes_trade_value():
    result = TradeCostAnalysis.evaluate(
        trade_value=100.0,
        fee_percent=100.0,
    )

    assert result.valid is False
    assert result.fee_amount == 100.0
    assert result.net_value == 0.0
    assert result.reason == "fee_consumes_trade_value"


def test_invalid_trade_value_preserves_uncalculated_costs_as_unknown():
    result = TradeCostAnalysis.evaluate(
        trade_value=0.0,
        fee_percent=0.1,
    )

    assert result.valid is False
    assert result.fee_amount is None
    assert result.net_value is None
    assert result.reason == "invalid_trade_value"


def test_invalid_fee_percent_preserves_uncalculated_costs_as_unknown():
    result = TradeCostAnalysis.evaluate(
        trade_value=1000.0,
        fee_percent=-0.1,
    )

    assert result.valid is False
    assert result.fee_amount is None
    assert result.net_value is None
    assert result.reason == "invalid_fee_percent"


def test_calculated_zero_fee_remains_numeric_zero():
    result = TradeCostAnalysis.evaluate(
        trade_value=1000.0,
        fee_percent=0.0,
    )

    assert result.valid is True
    assert result.fee_amount == 0.0
    assert result.net_value == 1000.0


@pytest.mark.parametrize(
    "trade_value",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
    ],
)
def test_invalid_trade_value_numeric_contract(trade_value):
    result = TradeCostAnalysis.evaluate(
        trade_value=trade_value,
        fee_percent=0.1,
    )

    assert result.valid is False
    assert result.reason == "invalid_trade_value"


@pytest.mark.parametrize(
    "fee_percent",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
    ],
)
def test_invalid_fee_percent_numeric_contract(fee_percent):
    result = TradeCostAnalysis.evaluate(
        trade_value=1000.0,
        fee_percent=fee_percent,
    )

    assert result.valid is False
    assert result.reason == "invalid_fee_percent"
