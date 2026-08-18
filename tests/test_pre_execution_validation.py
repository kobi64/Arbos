import pytest

from exchanges.pre_execution_validation import (
    PreExecutionValidationPipeline,
)


@pytest.fixture
def validator():
    return PreExecutionValidationPipeline()


def valid_order():
    return {
        "symbol": "BTC/USDT",
        "side": "buy",
        "order_type": "market",
        "quantity": 0.01,
        "price": None,
    }


def test_valid_market_order_passes(validator):
    result = validator.validate(valid_order())

    assert result["valid"] is True
    assert result["reasons"] == []


def test_valid_limit_order_passes(validator):
    order = valid_order()
    order["order_type"] = "limit"
    order["price"] = 62000.0

    result = validator.validate(order)

    assert result["valid"] is True


def test_missing_symbol_is_rejected(validator):
    order = valid_order()
    del order["symbol"]

    result = validator.validate(order)

    assert result["valid"] is False
    assert "MISSING_SYMBOL" in result["reasons"]


def test_invalid_symbol_format_is_rejected(validator):
    order = valid_order()
    order["symbol"] = "BTCUSDT"

    result = validator.validate(order)

    assert result["valid"] is False
    assert "INVALID_SYMBOL_FORMAT" in result["reasons"]


def test_invalid_side_is_rejected(validator):
    order = valid_order()
    order["side"] = "hold"

    result = validator.validate(order)

    assert result["valid"] is False
    assert "INVALID_SIDE" in result["reasons"]


def test_invalid_order_type_is_rejected(validator):
    order = valid_order()
    order["order_type"] = "iceberg"

    result = validator.validate(order)

    assert result["valid"] is False
    assert "INVALID_ORDER_TYPE" in result["reasons"]


def test_non_positive_quantity_is_rejected(validator):
    order = valid_order()
    order["quantity"] = 0

    result = validator.validate(order)

    assert result["valid"] is False
    assert "INVALID_QUANTITY" in result["reasons"]


def test_limit_order_requires_positive_price(validator):
    order = valid_order()
    order["order_type"] = "limit"
    order["price"] = None

    result = validator.validate(order)

    assert result["valid"] is False
    assert "LIMIT_PRICE_REQUIRED" in result["reasons"]


def test_market_order_does_not_require_price(validator):
    order = valid_order()
    order["price"] = None

    result = validator.validate(order)

    assert result["valid"] is True


def test_none_order_is_rejected(validator):
    with pytest.raises(ValueError, match="order is required"):
        validator.validate(None)


@pytest.mark.parametrize(
    "quantity",
    [
        float("inf"),
        float("-inf"),
        float("nan"),
    ],
)
def test_non_finite_quantity_is_rejected(quantity):
    pipeline = PreExecutionValidationPipeline()

    order = {
        "symbol": "BTC/USDT",
        "side": "buy",
        "order_type": "market",
        "quantity": quantity,
    }

    result = pipeline.validate(order)

    assert result["valid"] is False
    assert "INVALID_QUANTITY" in result["reasons"]


@pytest.mark.parametrize(
    "price",
    [
        float("inf"),
        float("-inf"),
        float("nan"),
    ],
)
def test_non_finite_limit_price_is_rejected(price):
    pipeline = PreExecutionValidationPipeline()

    order = {
        "symbol": "BTC/USDT",
        "side": "buy",
        "order_type": "limit",
        "quantity": 1.0,
        "price": price,
    }

    result = pipeline.validate(order)

    assert result["valid"] is False
    assert "LIMIT_PRICE_REQUIRED" in result["reasons"]


def test_boolean_quantity_is_rejected():
    pipeline = PreExecutionValidationPipeline()

    result = pipeline.validate(
        {
            "symbol": "BTC/USDT",
            "side": "buy",
            "order_type": "market",
            "quantity": True,
        }
    )

    assert result["valid"] is False
    assert "INVALID_QUANTITY" in result["reasons"]


def test_boolean_limit_price_is_rejected():
    pipeline = PreExecutionValidationPipeline()

    result = pipeline.validate(
        {
            "symbol": "BTC/USDT",
            "side": "buy",
            "order_type": "limit",
            "quantity": 1.0,
            "price": True,
        }
    )

    assert result["valid"] is False
    assert "LIMIT_PRICE_REQUIRED" in result["reasons"]
