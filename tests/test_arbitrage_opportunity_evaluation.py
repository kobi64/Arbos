from exchanges.arbitrage_opportunity_evaluation import (
    ArbitrageOpportunityEvaluation,
)


def test_accepts_executable_profitable_opportunity():
    result = ArbitrageOpportunityEvaluation.evaluate(
        route_feasible=True,
        starting_value=1000.0,
        final_value=1050.0,
        minimum_profit_percent=2.0,
    )

    assert result.valid is True
    assert result.executable is True
    assert result.net_profit == 50.0
    assert result.profit_percent == 5.0
    assert result.reason == "ok"


def test_rejects_infeasible_route():
    result = ArbitrageOpportunityEvaluation.evaluate(
        route_feasible=False,
        starting_value=1000.0,
        final_value=1050.0,
        minimum_profit_percent=2.0,
    )

    assert result.valid is True
    assert result.executable is False
    assert result.reason == "route_not_feasible"


def test_rejects_invalid_starting_value():
    result = ArbitrageOpportunityEvaluation.evaluate(
        route_feasible=True,
        starting_value=0.0,
        final_value=1050.0,
        minimum_profit_percent=2.0,
    )

    assert result.valid is False
    assert result.executable is False
    assert result.reason == "invalid_starting_value"


def test_rejects_negative_final_value():
    result = ArbitrageOpportunityEvaluation.evaluate(
        route_feasible=True,
        starting_value=1000.0,
        final_value=-1.0,
        minimum_profit_percent=2.0,
    )

    assert result.valid is False
    assert result.executable is False
    assert result.reason == "invalid_final_value"


def test_rejects_negative_minimum_profit_percent():
    result = ArbitrageOpportunityEvaluation.evaluate(
        route_feasible=True,
        starting_value=1000.0,
        final_value=1050.0,
        minimum_profit_percent=-1.0,
    )

    assert result.valid is False
    assert result.executable is False
    assert result.reason == "invalid_minimum_profit_percent"


def test_rejects_opportunity_below_profit_threshold():
    result = ArbitrageOpportunityEvaluation.evaluate(
        route_feasible=True,
        starting_value=1000.0,
        final_value=1010.0,
        minimum_profit_percent=2.0,
    )

    assert result.valid is True
    assert result.executable is False
    assert result.net_profit == 10.0
    assert result.profit_percent == 1.0
    assert result.reason == "below_minimum_profit"


def test_accepts_opportunity_exactly_at_threshold():
    result = ArbitrageOpportunityEvaluation.evaluate(
        route_feasible=True,
        starting_value=1000.0,
        final_value=1020.0,
        minimum_profit_percent=2.0,
    )

    assert result.valid is True
    assert result.executable is True
    assert result.net_profit == 20.0
    assert result.profit_percent == 2.0
    assert result.reason == "ok"


def test_rejects_loss_making_opportunity():
    result = ArbitrageOpportunityEvaluation.evaluate(
        route_feasible=True,
        starting_value=1000.0,
        final_value=950.0,
        minimum_profit_percent=2.0,
    )

    assert result.valid is True
    assert result.executable is False
    assert result.net_profit == -50.0
    assert result.profit_percent == -5.0
    assert result.reason == "below_minimum_profit"
