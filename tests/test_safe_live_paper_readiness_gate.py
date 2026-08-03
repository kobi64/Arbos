import pytest

from exchanges.safe_live_paper_readiness_gate import (
    SafeLivePaperReadinessGate,
)


@pytest.fixture
def gate():
    return SafeLivePaperReadinessGate()


def valid_opportunity():
    return {
        "opportunity_id": "OPP-081",
        "legs": [
            {
                "symbol": "BTC/USDT",
                "side": "buy",
                "quantity": 0.01,
                "order_type": "market",
            },
            {
                "symbol": "ETH/BTC",
                "side": "buy",
                "quantity": 0.2,
                "order_type": "market",
            },
        ],
    }


def ready_kwargs():
    return {
        "exchange_connected": True,
        "account_valid": True,
        "trading_pair_active": True,
        "sufficient_balance": True,
        "gas_available": True,
        "withdrawal_enabled": True,
        "approval_granted": True,
    }


def test_ready_opportunity_passes(gate):
    result = gate.evaluate(
        opportunity=valid_opportunity(),
        **ready_kwargs(),
    )

    assert result["ready"] is True
    assert result["reason"] == (
        "ready_for_safe_live_paper_execution"
    )


def test_invalid_order_is_blocked(gate):
    opportunity = valid_opportunity()
    opportunity["legs"][0]["quantity"] = 0

    result = gate.evaluate(
        opportunity=opportunity,
        **ready_kwargs(),
    )

    assert result["ready"] is False
    assert result["reason"] == "order_validation_failed"
    assert result["leg_number"] == 1
    assert "INVALID_QUANTITY" in result["validation_reasons"]


def test_failed_readiness_is_blocked(gate):
    checks = ready_kwargs()
    checks["exchange_connected"] = False

    result = gate.evaluate(
        opportunity=valid_opportunity(),
        **checks,
    )

    assert result["ready"] is False
    assert result["reason"] == "exchange_not_connected"


def test_missing_approval_is_blocked(gate):
    checks = ready_kwargs()
    checks["approval_granted"] = False

    result = gate.evaluate(
        opportunity=valid_opportunity(),
        **checks,
    )

    assert result["ready"] is False
    assert result["reason"] == "approval_required"


def test_missing_opportunity_raises(gate):
    with pytest.raises(ValueError, match="opportunity is required"):
        gate.evaluate(
            opportunity=None,
            **ready_kwargs(),
        )


def test_history_records_result(gate):
    gate.evaluate(
        opportunity=valid_opportunity(),
        **ready_kwargs(),
    )

    assert len(gate.history()) == 1
