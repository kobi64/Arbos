import pytest

from exchanges.paper_route_profitability_gate import (
    PaperRouteProfitabilityGate,
)


@pytest.fixture
def gate():
    return PaperRouteProfitabilityGate()


def test_profitable_route_is_accepted(gate):
    result = gate.evaluate({
        "profitable": True,
        "net_profit": 40.0,
        "profit_percent": 4.0,
        "reason": "ok",
    })

    assert result["accepted"] is True
    assert result["reason"] == "ok"


def test_unprofitable_route_is_rejected(gate):
    result = gate.evaluate({
        "profitable": False,
        "net_profit": 5.0,
        "profit_percent": 0.5,
        "reason": "below_minimum_profit",
    })

    assert result["accepted"] is False
    assert result["reason"] == "below_minimum_profit"


def test_gate_preserves_profit_details(gate):
    result = gate.evaluate({
        "profitable": True,
        "net_profit": 40.0,
        "profit_percent": 4.0,
        "reason": "ok",
    })

    assert result["net_profit"] == 40.0
    assert result["profit_percent"] == 4.0


def test_missing_pnl_result_is_rejected(gate):
    with pytest.raises(ValueError, match="pnl_result is required"):
        gate.evaluate(None)


def test_missing_profitable_flag_is_rejected(gate):
    with pytest.raises(ValueError, match="profitable is required"):
        gate.evaluate({
            "net_profit": 10.0,
            "profit_percent": 1.0,
            "reason": "ok",
        })


def test_missing_profit_percent_is_rejected(gate):
    with pytest.raises(ValueError, match="profit_percent is required"):
        gate.evaluate({
            "profitable": True,
            "net_profit": 10.0,
            "reason": "ok",
        })


def test_missing_net_profit_is_rejected(gate):
    with pytest.raises(ValueError, match="net_profit is required"):
        gate.evaluate({
            "profitable": True,
            "profit_percent": 1.0,
            "reason": "ok",
        })


@pytest.mark.parametrize(
    "profitable",
    [
        None,
        0,
        1,
        "true",
        "false",
        "yes",
        [],
        {},
    ],
)
def test_profitable_flag_requires_real_boolean(
    gate,
    profitable,
):
    with pytest.raises(
        ValueError,
        match="profitable must be a boolean",
    ):
        gate.evaluate({
            "profitable": profitable,
            "net_profit": 10.0,
            "profit_percent": 1.0,
            "reason": "ok",
        })


@pytest.mark.parametrize(
    "field,value",
    [
        ("net_profit", None),
        ("net_profit", "bad"),
        ("net_profit", float("nan")),
        ("net_profit", float("inf")),
        ("net_profit", float("-inf")),
        ("net_profit", True),
        ("profit_percent", None),
        ("profit_percent", "bad"),
        ("profit_percent", float("nan")),
        ("profit_percent", float("inf")),
        ("profit_percent", float("-inf")),
        ("profit_percent", True),
    ],
)
def test_profitability_numbers_must_be_finite(
    gate,
    field,
    value,
):
    record = {
        "profitable": True,
        "net_profit": 10.0,
        "profit_percent": 1.0,
        "reason": "ok",
    }
    record[field] = value

    with pytest.raises(
        ValueError,
        match=f"{field} must be a finite number",
    ):
        gate.evaluate(record)


@pytest.mark.parametrize(
    "field,value",
    [
        ("net_profit", 0.0),
        ("net_profit", -0.01),
        ("profit_percent", 0.0),
        ("profit_percent", -0.01),
    ],
)
def test_profitable_true_requires_positive_economics(
    gate,
    field,
    value,
):
    record = {
        "profitable": True,
        "net_profit": 10.0,
        "profit_percent": 1.0,
        "reason": "ok",
    }
    record[field] = value

    result = gate.evaluate(record)

    assert result["accepted"] is False
    assert result["reason"] == "invalid_profitable_economics"


def test_numeric_string_profitability_values_remain_supported(
    gate,
):
    result = gate.evaluate({
        "profitable": True,
        "net_profit": "10.5",
        "profit_percent": "1.25",
        "reason": "ok",
    })

    assert result["accepted"] is True
    assert result["net_profit"] == 10.5
    assert result["profit_percent"] == 1.25
