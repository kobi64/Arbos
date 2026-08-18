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




def test_empty_buy_book_is_rejected_as_unavailable(engine):
    with pytest.raises(
        ValueError,
        match="order book unavailable",
    ):
        engine.evaluate(
            side="buy",
            quantity=1.0,
            order_book={
                "asks": [],
                "bids": [],
            },
        )


def test_empty_sell_book_is_rejected_as_unavailable(engine):
    with pytest.raises(
        ValueError,
        match="order book unavailable",
    ):
        engine.evaluate(
            side="sell",
            quantity=1.0,
            order_book={
                "asks": [],
                "bids": [],
            },
        )


def test_partial_fill_preserves_numeric_average_price_and_slippage(engine):
    result = engine.evaluate(
        side="buy",
        quantity=10.0,
        order_book={
            "asks": [
                [100.0, 2.0],
                [101.0, 2.0],
            ],
            "bids": [],
        },
    )

    assert result["filled_quantity"] == 4.0
    assert result["total_value"] == 402.0

    # A genuine partial execution occurred.
    assert result["average_price"] == 100.5
    assert result["slippage_percent"] == pytest.approx(
        ((100.5 - 100.0) / 100.0) * 100
    )

    assert result["reason"] == "insufficient_liquidity"


def test_single_level_fill_can_have_genuine_zero_slippage(engine):
    result = engine.evaluate(
        side="buy",
        quantity=1.0,
        order_book={
            "asks": [
                [100.0, 5.0],
            ],
            "bids": [],
        },
    )

    assert result["filled_quantity"] == 1.0
    assert result["total_value"] == 100.0
    assert result["average_price"] == 100.0

    # This is a real measured zero.
    assert result["slippage_percent"] == 0.0

    # Successful evaluation has no failure reason.
    assert result["reason"] is None


@pytest.mark.parametrize(
    "quantity",
    [
        "nan",
        "inf",
        "-inf",
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_non_finite_quantity_is_rejected(engine, quantity):
    with pytest.raises(
        ValueError,
        match="quantity must be positive",
    ):
        engine.evaluate(
            side="buy",
            quantity=quantity,
            order_book=sample_book(),
        )


@pytest.mark.parametrize(
    "price",
    [
        0.0,
        -1.0,
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_invalid_order_book_price_is_rejected(engine, price):
    book = sample_book()
    book["asks"][0][0] = price

    with pytest.raises(
        ValueError,
        match="invalid order book level",
    ):
        engine.evaluate(
            side="buy",
            quantity=1.0,
            order_book=book,
        )


@pytest.mark.parametrize(
    "available",
    [
        -1.0,
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_invalid_order_book_available_quantity_is_rejected(
    engine,
    available,
):
    book = sample_book()
    book["asks"][0][1] = available

    with pytest.raises(
        ValueError,
        match="invalid order book level",
    ):
        engine.evaluate(
            side="buy",
            quantity=1.0,
            order_book=book,
        )


def test_numeric_string_depth_values_are_normalized(engine):
    result = engine.evaluate(
        side="buy",
        quantity="2",
        order_book={
            "asks": [
                ["100", "1"],
                ["101", "2"],
            ],
            "bids": [],
        },
    )

    assert result["requested_quantity"] == 2.0
    assert result["filled_quantity"] == 2.0
    assert result["best_price"] == 100.0
    assert result["average_price"] == 100.5
    assert result["total_value"] == 201.0


def test_zero_available_level_is_valid_but_not_executed(engine):
    result = engine.evaluate(
        side="buy",
        quantity=1.0,
        order_book={
            "asks": [
                [100.0, 0.0],
                [101.0, 2.0],
            ],
            "bids": [],
        },
    )

    assert result["filled"] is True
    assert result["filled_quantity"] == 1.0
    assert result["average_price"] == 101.0
    assert result["total_value"] == 101.0


def test_no_executable_liquidity_preserves_numeric_zero_outputs(engine):
    result = engine.evaluate(
        side="buy",
        quantity=1.0,
        order_book={
            "asks": [
                [100.0, 0.0],
                [101.0, 0.0],
            ],
            "bids": [],
        },
    )

    assert result["filled"] is False
    assert result["reason"] == "insufficient_liquidity"
    assert result["filled_quantity"] == 0.0
    assert result["average_price"] == 0.0
    assert result["slippage_percent"] == 0.0
    assert result["total_value"] == 0.0
