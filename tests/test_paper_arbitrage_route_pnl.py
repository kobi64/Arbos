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
