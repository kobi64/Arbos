from exchanges.arbitrage_cost_analysis import ArbitrageCostAnalysis


def test_calculates_total_arbitrage_cost():
    result = ArbitrageCostAnalysis.evaluate(
        starting_value=1000.0,
        buy_fee_percent=0.1,
        transfer_fee=2.0,
        sell_fee_percent=0.1,
    )

    assert result.valid is True
    assert result.buy_fee == 1.0
    assert result.transfer_fee == 2.0
    assert result.sell_fee == 0.997
    assert result.total_cost == 3.997
    assert result.final_value == 996.003
    assert result.reason == "ok"


def test_rejects_invalid_starting_value():
    result = ArbitrageCostAnalysis.evaluate(
        starting_value=0.0,
        buy_fee_percent=0.1,
        transfer_fee=2.0,
        sell_fee_percent=0.1,
    )

    assert result.valid is False
    assert result.reason == "invalid_starting_value"


def test_rejects_negative_buy_fee_percent():
    result = ArbitrageCostAnalysis.evaluate(
        starting_value=1000.0,
        buy_fee_percent=-0.1,
        transfer_fee=2.0,
        sell_fee_percent=0.1,
    )

    assert result.valid is False
    assert result.reason == "invalid_buy_fee_percent"


def test_rejects_negative_sell_fee_percent():
    result = ArbitrageCostAnalysis.evaluate(
        starting_value=1000.0,
        buy_fee_percent=0.1,
        transfer_fee=2.0,
        sell_fee_percent=-0.1,
    )

    assert result.valid is False
    assert result.reason == "invalid_sell_fee_percent"


def test_rejects_negative_transfer_fee():
    result = ArbitrageCostAnalysis.evaluate(
        starting_value=1000.0,
        buy_fee_percent=0.1,
        transfer_fee=-2.0,
        sell_fee_percent=0.1,
    )

    assert result.valid is False
    assert result.reason == "invalid_transfer_fee"


def test_rejects_when_costs_consume_value():
    result = ArbitrageCostAnalysis.evaluate(
        starting_value=100.0,
        buy_fee_percent=50.0,
        transfer_fee=60.0,
        sell_fee_percent=0.1,
    )

    assert result.valid is False
    assert result.reason == "costs_consume_value"


def test_invalid_starting_value_preserves_uncalculated_costs_as_unknown():
    result = ArbitrageCostAnalysis.evaluate(
        starting_value=0.0,
        buy_fee_percent=0.1,
        transfer_fee=2.0,
        sell_fee_percent=0.1,
    )

    assert result.valid is False
    assert result.buy_fee is None
    assert result.transfer_fee is None
    assert result.sell_fee is None
    assert result.total_cost is None
    assert result.final_value is None
    assert result.reason == "invalid_starting_value"


def test_invalid_fee_input_preserves_uncalculated_costs_as_unknown():
    result = ArbitrageCostAnalysis.evaluate(
        starting_value=1000.0,
        buy_fee_percent=-0.1,
        transfer_fee=2.0,
        sell_fee_percent=0.1,
    )

    assert result.valid is False
    assert result.buy_fee is None
    assert result.transfer_fee is None
    assert result.sell_fee is None
    assert result.total_cost is None
    assert result.final_value is None
    assert result.reason == "invalid_buy_fee_percent"


def test_pre_sell_failure_preserves_only_calculated_costs():
    result = ArbitrageCostAnalysis.evaluate(
        starting_value=100.0,
        buy_fee_percent=50.0,
        transfer_fee=60.0,
        sell_fee_percent=0.1,
    )

    assert result.valid is False

    assert result.buy_fee == 50.0
    assert result.transfer_fee == 60.0

    # Sell leg never occurred.
    assert result.sell_fee is None

    assert result.total_cost == 110.0
    assert result.final_value == 0.0
    assert result.reason == "costs_consume_value"


def test_genuine_zero_cost_arbitrage_preserves_numeric_zero():
    result = ArbitrageCostAnalysis.evaluate(
        starting_value=1000.0,
        buy_fee_percent=0.0,
        transfer_fee=0.0,
        sell_fee_percent=0.0,
    )

    assert result.valid is True
    assert result.buy_fee == 0.0
    assert result.transfer_fee == 0.0
    assert result.sell_fee == 0.0
    assert result.total_cost == 0.0
    assert result.final_value == 1000.0
    assert result.reason == "ok"
