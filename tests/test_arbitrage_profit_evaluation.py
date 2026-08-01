from exchanges.arbitrage_profit_evaluation import ArbitrageProfitEvaluation


def test_calculates_net_profit_and_percent():
    result = ArbitrageProfitEvaluation.evaluate(
        starting_value=1000.0,
        final_value=1050.0,
        minimum_profit_percent=2.0,
    )

    assert result.valid is True
    assert result.profitable is True
    assert result.net_profit == 50.0
    assert result.profit_percent == 5.0
    assert result.reason == "ok"


def test_rejects_invalid_starting_value():
    result = ArbitrageProfitEvaluation.evaluate(
        starting_value=0.0,
        final_value=1050.0,
        minimum_profit_percent=2.0,
    )

    assert result.valid is False
    assert result.reason == "invalid_starting_value"


def test_rejects_negative_final_value():
    result = ArbitrageProfitEvaluation.evaluate(
        starting_value=1000.0,
        final_value=-10.0,
        minimum_profit_percent=2.0,
    )

    assert result.valid is False
    assert result.reason == "invalid_final_value"


def test_rejects_negative_minimum_profit_percent():
    result = ArbitrageProfitEvaluation.evaluate(
        starting_value=1000.0,
        final_value=1050.0,
        minimum_profit_percent=-1.0,
    )

    assert result.valid is False
    assert result.reason == "invalid_minimum_profit_percent"


def test_marks_trade_unprofitable_below_threshold():
    result = ArbitrageProfitEvaluation.evaluate(
        starting_value=1000.0,
        final_value=1010.0,
        minimum_profit_percent=2.0,
    )

    assert result.valid is True
    assert result.profitable is False
    assert result.net_profit == 10.0
    assert result.profit_percent == 1.0
    assert result.reason == "below_minimum_profit"


def test_accepts_profit_exactly_at_threshold():
    result = ArbitrageProfitEvaluation.evaluate(
        starting_value=1000.0,
        final_value=1020.0,
        minimum_profit_percent=2.0,
    )

    assert result.valid is True
    assert result.profitable is True
    assert result.net_profit == 20.0
    assert result.profit_percent == 2.0
    assert result.reason == "ok"


def test_marks_loss_as_unprofitable():
    result = ArbitrageProfitEvaluation.evaluate(
        starting_value=1000.0,
        final_value=950.0,
        minimum_profit_percent=2.0,
    )

    assert result.valid is True
    assert result.profitable is False
    assert result.net_profit == -50.0
    assert result.profit_percent == -5.0
    assert result.reason == "below_minimum_profit"
