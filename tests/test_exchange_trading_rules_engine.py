import pytest

from exchanges.exchange_trading_rules_engine import (
    ExchangeTradingRulesEngine,
)


@pytest.fixture
def engine():
    return ExchangeTradingRulesEngine()


def sample_rules():
    return {
        "min_quantity": 0.001,
        "max_quantity": 10.0,
        "quantity_step": 0.001,
        "price_tick": 0.1,
        "min_notional": 10.0,
    }


def test_accepts_valid_order(engine):
    result = engine.validate(
        quantity=0.125,
        price=100.0,
        rules=sample_rules(),
    )

    assert result["valid"] is True
    assert result["reason"] is None


def test_rejects_quantity_below_minimum(engine):
    result = engine.validate(
        quantity=0.0005,
        price=100.0,
        rules=sample_rules(),
    )

    assert result["valid"] is False
    assert result["reason"] == "below_min_quantity"


def test_rejects_notional_below_minimum(engine):
    result = engine.validate(
        quantity=0.05,
        price=100.0,
        rules=sample_rules(),
    )

    assert result["valid"] is False
    assert result["reason"] == "below_min_notional"


def test_rejects_quantity_above_maximum(engine):
    result = engine.validate(
        quantity=10.001,
        price=100.0,
        rules=sample_rules(),
    )

    assert result["valid"] is False
    assert result["reason"] == "above_max_quantity"


def test_rejects_invalid_quantity_step(engine):
    result = engine.validate(
        quantity=0.1255,
        price=100.0,
        rules=sample_rules(),
    )

    assert result["valid"] is False
    assert result["reason"] == "invalid_quantity_step"


def test_rejects_invalid_price_tick(engine):
    result = engine.validate(
        quantity=0.125,
        price=100.05,
        rules=sample_rules(),
    )

    assert result["valid"] is False
    assert result["reason"] == "invalid_price_tick"


def test_rejects_non_positive_quantity(engine):
    with pytest.raises(ValueError, match="quantity must be positive"):
        engine.validate(
            quantity=0.0,
            price=100.0,
            rules=sample_rules(),
        )


def test_rejects_non_positive_price(engine):
    with pytest.raises(ValueError, match="price must be positive"):
        engine.validate(
            quantity=0.125,
            price=0.0,
            rules=sample_rules(),
        )


@pytest.mark.parametrize(
    "quantity",
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
def test_rejects_invalid_numeric_quantity(engine, quantity):
    with pytest.raises(
        ValueError,
        match="quantity must be positive",
    ):
        engine.validate(
            quantity=quantity,
            price=100.0,
            rules=sample_rules(),
        )


@pytest.mark.parametrize(
    "price",
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
def test_rejects_invalid_numeric_price(engine, price):
    with pytest.raises(
        ValueError,
        match="price must be positive",
    ):
        engine.validate(
            quantity=0.125,
            price=price,
            rules=sample_rules(),
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("min_quantity", float("nan")),
        ("min_quantity", float("inf")),
        ("min_quantity", -1.0),
        ("max_quantity", float("nan")),
        ("max_quantity", float("inf")),
        ("max_quantity", 0.0),
        ("quantity_step", float("nan")),
        ("quantity_step", float("inf")),
        ("quantity_step", 0.0),
        ("quantity_step", -1.0),
        ("price_tick", float("nan")),
        ("price_tick", float("inf")),
        ("price_tick", 0.0),
        ("price_tick", -1.0),
        ("min_notional", float("nan")),
        ("min_notional", float("inf")),
        ("min_notional", -1.0),
    ],
)
def test_rejects_invalid_numeric_rule_values(
    engine,
    field,
    value,
):
    rules = sample_rules()
    rules[field] = value

    with pytest.raises(ValueError):
        engine.validate(
            quantity=0.125,
            price=100.0,
            rules=rules,
        )


def test_rejects_max_quantity_below_min_quantity(engine):
    rules = sample_rules()
    rules["min_quantity"] = 1.0
    rules["max_quantity"] = 0.5

    with pytest.raises(ValueError):
        engine.validate(
            quantity=0.125,
            price=100.0,
            rules=rules,
        )
