import pytest

from exchanges.order_book_liquidity_slippage_engine import (
    OrderBookLiquiditySlippageEngine,
)


@pytest.fixture
def engine():
    return OrderBookLiquiditySlippageEngine()


def sample_book():
    return {
        "bids": [[100.0, 2.0], [99.0, 3.0]],
        "asks": [[101.0, 1.5], [102.0, 4.0]],
    }


def test_buy_walks_ask_levels_and_calculates_weighted_price(engine):
    result = engine.evaluate(
        side="buy",
        quantity=2.0,
        order_book=sample_book(),
    )

    expected = ((1.5 * 101.0) + (0.5 * 102.0)) / 2.0
    assert result["filled"] is True
    assert result["filled_quantity"] == 2.0
    assert result["average_price"] == pytest.approx(expected)


def test_sell_walks_bid_levels_and_calculates_weighted_price(engine):
    result = engine.evaluate(
        side="sell",
        quantity=4.0,
        order_book=sample_book(),
    )

    expected = ((2.0 * 100.0) + (2.0 * 99.0)) / 4.0
    assert result["filled"] is True
    assert result["filled_quantity"] == 4.0
    assert result["average_price"] == pytest.approx(expected)


def test_rejects_when_order_book_cannot_fill_quantity(engine):
    result = engine.evaluate(
        side="buy",
        quantity=10.0,
        order_book=sample_book(),
    )

    assert result["filled"] is False
    assert result["reason"] == "insufficient_liquidity"
    assert result["filled_quantity"] == 5.5


def test_calculates_slippage_from_best_price(engine):
    result = engine.evaluate(
        side="buy",
        quantity=2.0,
        order_book=sample_book(),
    )

    expected_average = ((1.5 * 101.0) + (0.5 * 102.0)) / 2.0
    expected_slippage = ((expected_average - 101.0) / 101.0) * 100

    assert result["best_price"] == 101.0
    assert result["slippage_percent"] == pytest.approx(expected_slippage)


def test_calculates_slippage_from_best_price(engine):
    result = engine.evaluate(
        side="buy",
        quantity=2.0,
        order_book=sample_book(),
    )

    expected_average = ((1.5 * 101.0) + (0.5 * 102.0)) / 2.0
    expected_slippage = ((expected_average - 101.0) / 101.0) * 100

    assert result["best_price"] == 101.0
    assert result["slippage_percent"] == pytest.approx(expected_slippage)


def test_rejects_invalid_side(engine):
    with pytest.raises(ValueError, match="invalid side"):
        engine.evaluate(
            side="hold",
            quantity=1.0,
            order_book=sample_book(),
        )


def test_rejects_non_positive_quantity(engine):
    with pytest.raises(ValueError, match="quantity must be positive"):
        engine.evaluate(
            side="buy",
            quantity=0.0,
            order_book=sample_book(),
        )
