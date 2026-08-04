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
