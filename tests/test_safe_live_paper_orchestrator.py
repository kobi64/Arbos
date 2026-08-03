import pytest

from exchanges.safe_live_paper_orchestrator import (
    SafeLivePaperOrchestrator,
)


class FakeLiveMarketDataProvider:
    def __init__(self):
        self.prices = {
            "BTC/USDT": 62000.0,
            "ETH/BTC": 0.05,
            "ETH/USDT": 3200.0,
        }

    def get_price(self, symbol):
        return self.prices.get(symbol)


@pytest.fixture
def orchestrator():
    return SafeLivePaperOrchestrator(
        FakeLiveMarketDataProvider()
    )


def valid_opportunity():
    return {
        "opportunity_id": "OPP-082",
        "legs": [
            {"symbol": "BTC/USDT", "side": "buy", "quantity": 0.01},
            {"symbol": "ETH/BTC", "side": "buy", "quantity": 0.2},
            {"symbol": "ETH/USDT", "side": "sell", "quantity": 0.2},
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


def economics_kwargs():
    return {
        "starting_value": 1000.0,
        "gross_final_value": 1050.0,
        "trading_fees": 5.0,
        "transfer_fees": 2.0,
        "other_costs": 3.0,
        "minimum_profit_percent": 2.0,
    }


def test_ready_profitable_opportunity_executes(orchestrator):
    result = orchestrator.execute(
        opportunity=valid_opportunity(),
        **economics_kwargs(),
        **ready_kwargs(),
    )

    assert result["ready"] is True
    assert result["execution"] is not None
    assert result["execution"]["status"] == "COMPLETED"


def test_failed_readiness_blocks_execution(orchestrator):
    checks = ready_kwargs()
    checks["exchange_connected"] = False

    result = orchestrator.execute(
        opportunity=valid_opportunity(),
        **economics_kwargs(),
        **checks,
    )

    assert result["ready"] is False
    assert result["reason"] == "exchange_not_connected"
    assert result["execution"] is None


def test_missing_approval_blocks_execution(orchestrator):
    checks = ready_kwargs()
    checks["approval_granted"] = False

    result = orchestrator.execute(
        opportunity=valid_opportunity(),
        **economics_kwargs(),
        **checks,
    )

    assert result["ready"] is False
    assert result["reason"] == "approval_required"
    assert result["execution"] is None


def test_unprofitable_ready_opportunity_does_not_execute(orchestrator):
    economics = economics_kwargs()
    economics["gross_final_value"] = 1010.0

    result = orchestrator.execute(
        opportunity=valid_opportunity(),
        **economics,
        **ready_kwargs(),
    )

    assert result["ready"] is True
    assert result["result"]["accepted"] is False
    assert result["execution"] is None


def test_history_records_result(orchestrator):
    orchestrator.execute(
        opportunity=valid_opportunity(),
        **economics_kwargs(),
        **ready_kwargs(),
    )

    assert len(orchestrator.history()) == 1
