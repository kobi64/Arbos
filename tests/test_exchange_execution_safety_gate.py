import pytest

from exchanges.exchange_execution_safety_gate import (
    ExchangeExecutionSafetyGate,
)


@pytest.fixture
def gate():
    return ExchangeExecutionSafetyGate()


def valid_context():
    return {
        "exchange_healthy": True,
        "market_data_fresh": True,
        "sufficient_balance": True,
        "valid_order_size": True,
        "network_supported": True,
        "reconciliation_clear": True,
    }


def test_valid_execution_is_allowed(gate):
    result = gate.evaluate(valid_context())

    assert result["allowed"] is True
    assert result["reasons"] == []


@pytest.mark.parametrize(
    "field,reason",
    [
        ("exchange_healthy", "EXCHANGE_UNHEALTHY"),
        ("market_data_fresh", "STALE_MARKET_DATA"),
        ("sufficient_balance", "INSUFFICIENT_BALANCE"),
        ("valid_order_size", "INVALID_ORDER_SIZE"),
        ("network_supported", "NETWORK_UNSUPPORTED"),
        ("reconciliation_clear", "RECONCILIATION_REQUIRED"),
    ],
)
def test_failed_safety_condition_blocks_execution(gate, field, reason):
    context = valid_context()
    context[field] = False

    result = gate.evaluate(context)

    assert result["allowed"] is False
    assert reason in result["reasons"]


def test_multiple_failures_are_reported(gate):
    context = valid_context()
    context["exchange_healthy"] = False
    context["market_data_fresh"] = False
    context["reconciliation_clear"] = False

    result = gate.evaluate(context)

    assert result["allowed"] is False
    assert result["reasons"] == [
        "EXCHANGE_UNHEALTHY",
        "STALE_MARKET_DATA",
        "RECONCILIATION_REQUIRED",
    ]


def test_missing_safety_field_blocks_execution(gate):
    context = valid_context()
    del context["exchange_healthy"]

    result = gate.evaluate(context)

    assert result["allowed"] is False
    assert "MISSING_EXCHANGE_HEALTHY" in result["reasons"]


def test_none_context_is_rejected(gate):
    with pytest.raises(ValueError, match="context is required"):
        gate.evaluate(None)
