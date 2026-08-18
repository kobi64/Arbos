import pytest

from exchanges.paper_arbitrage_route_pnl import (
    PaperArbitrageRoutePnL,
)


@pytest.fixture
def pnl():
    return PaperArbitrageRoutePnL()


def test_calculates_net_final_value_after_costs(pnl):
    result = pnl.evaluate(
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    assert result["total_costs"] == 10.0
    assert result["net_final_value"] == 1040.0


def test_reports_net_profit_and_percent(pnl):
    result = pnl.evaluate(
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    assert result["net_profit"] == 40.0
    assert result["profit_percent"] == 4.0
    assert result["profitable"] is True


def test_fees_can_turn_gross_profit_into_unprofitable_trade(pnl):
    result = pnl.evaluate(
        starting_value=1000.0,
        gross_final_value=1030.0,
        trading_fees=15.0,
        transfer_fees=10.0,
        other_costs=5.0,
        minimum_profit_percent=2.0,
    )

    assert result["net_final_value"] == 1000.0
    assert result["net_profit"] == 0.0
    assert result["profitable"] is False


def test_negative_cost_is_rejected(pnl):
    with pytest.raises(ValueError, match="costs must be non-negative"):
        pnl.evaluate(
            starting_value=1000.0,
            gross_final_value=1050.0,
            trading_fees=-1.0,
            transfer_fees=0.0,
            other_costs=0.0,
            minimum_profit_percent=2.0,
        )


def test_invalid_starting_value_is_rejected(pnl):
    with pytest.raises(ValueError, match="starting_value must be positive"):
        pnl.evaluate(
            starting_value=0.0,
            gross_final_value=1050.0,
            trading_fees=0.0,
            transfer_fees=0.0,
            other_costs=0.0,
            minimum_profit_percent=2.0,
        )


def test_negative_gross_final_value_is_rejected(pnl):
    with pytest.raises(ValueError, match="gross_final_value must be non-negative"):
        pnl.evaluate(
            starting_value=1000.0,
            gross_final_value=-1.0,
            trading_fees=0.0,
            transfer_fees=0.0,
            other_costs=0.0,
            minimum_profit_percent=2.0,
        )


def test_negative_minimum_profit_percent_is_rejected(pnl):
    with pytest.raises(ValueError, match="minimum_profit_percent must be non-negative"):
        pnl.evaluate(
            starting_value=1000.0,
            gross_final_value=1050.0,
            trading_fees=0.0,
            transfer_fees=0.0,
            other_costs=0.0,
            minimum_profit_percent=-1.0,
        )


def test_profitability_threshold_matches_existing_evaluator(pnl):
    result = pnl.evaluate(
        starting_value=1000.0,
        gross_final_value=1025.0,
        trading_fees=5.0,
        transfer_fees=0.0,
        other_costs=0.0,
        minimum_profit_percent=2.0,
    )

    assert result["net_final_value"] == 1020.0
    assert result["profit_percent"] == 2.0
    assert result["profitable"] is True


def test_costs_exceeding_gross_value_do_not_report_zero_profit(pnl):
    result = pnl.evaluate(
        starting_value=1000.0,
        gross_final_value=10.0,
        trading_fees=20.0,
        transfer_fees=0.0,
        other_costs=0.0,
        minimum_profit_percent=2.0,
    )

    assert result["net_final_value"] == -10.0
    assert result["net_profit"] is None
    assert result["profit_percent"] is None
    assert result["profitable"] is False
    assert result["reason"] == "invalid_final_value"


@pytest.mark.parametrize(
    "starting_value",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
        0.0,
        -1.0,
    ],
)
def test_invalid_numeric_starting_values_are_rejected(
    pnl,
    starting_value,
):
    with pytest.raises(
        ValueError,
        match="starting_value must be positive",
    ):
        pnl.evaluate(
            starting_value=starting_value,
            gross_final_value=1050.0,
            trading_fees=0.0,
            transfer_fees=0.0,
            other_costs=0.0,
            minimum_profit_percent=2.0,
        )


@pytest.mark.parametrize(
    "gross_final_value",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
        -1.0,
    ],
)
def test_invalid_numeric_gross_final_values_are_rejected(
    pnl,
    gross_final_value,
):
    with pytest.raises(
        ValueError,
        match="gross_final_value must be non-negative",
    ):
        pnl.evaluate(
            starting_value=1000.0,
            gross_final_value=gross_final_value,
            trading_fees=0.0,
            transfer_fees=0.0,
            other_costs=0.0,
            minimum_profit_percent=2.0,
        )


@pytest.mark.parametrize(
    "minimum_profit_percent",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
        -1.0,
    ],
)
def test_invalid_numeric_minimum_profit_percent_values_are_rejected(
    pnl,
    minimum_profit_percent,
):
    with pytest.raises(
        ValueError,
        match="minimum_profit_percent must be non-negative",
    ):
        pnl.evaluate(
            starting_value=1000.0,
            gross_final_value=1050.0,
            trading_fees=0.0,
            transfer_fees=0.0,
            other_costs=0.0,
            minimum_profit_percent=minimum_profit_percent,
        )


@pytest.mark.parametrize(
    "field",
    [
        "trading_fees",
        "transfer_fees",
        "other_costs",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
        -1.0,
    ],
)
def test_invalid_numeric_cost_values_are_rejected(
    pnl,
    field,
    value,
):
    kwargs = {
        "starting_value": 1000.0,
        "gross_final_value": 1050.0,
        "trading_fees": 0.0,
        "transfer_fees": 0.0,
        "other_costs": 0.0,
        "minimum_profit_percent": 2.0,
    }
    kwargs[field] = value

    with pytest.raises(
        ValueError,
        match="costs must be non-negative",
    ):
        pnl.evaluate(**kwargs)


def test_numeric_strings_are_normalized_to_floats(pnl):
    result = pnl.evaluate(
        starting_value="1000",
        gross_final_value="1050",
        trading_fees="5",
        transfer_fees="2",
        other_costs="3",
        minimum_profit_percent="2",
    )

    assert result["starting_value"] == 1000.0
    assert result["gross_final_value"] == 1050.0
    assert result["trading_fees"] == 5.0
    assert result["transfer_fees"] == 2.0
    assert result["other_costs"] == 3.0
    assert result["total_costs"] == 10.0
    assert result["net_final_value"] == 1040.0
    assert result["profit_percent"] == 4.0


def test_zero_values_remain_valid_for_non_negative_fields(pnl):
    result = pnl.evaluate(
        starting_value=1000.0,
        gross_final_value=0.0,
        trading_fees=0.0,
        transfer_fees=0.0,
        other_costs=0.0,
        minimum_profit_percent=0.0,
    )

    assert result["gross_final_value"] == 0.0
    assert result["total_costs"] == 0.0
    assert result["net_final_value"] == 0.0
    assert result["profitable"] is False
