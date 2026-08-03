import pytest

from exchanges.live_paper_execution_coordinator import (
    LivePaperExecutionCoordinator,
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
def coordinator():
    return LivePaperExecutionCoordinator(
        FakeLiveMarketDataProvider()
    )


def valid_route():
    return {
        "route_id": "ROUTE-001",
        "legs": [
            {"symbol": "BTC/USDT", "side": "buy", "quantity": 0.01},
            {"symbol": "ETH/BTC", "side": "buy", "quantity": 0.2},
            {"symbol": "ETH/USDT", "side": "sell", "quantity": 0.2},
        ],
    }


def test_profitable_route_is_executed(coordinator):
    result = coordinator.execute(
        route=valid_route(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    assert result["accepted"] is True
    assert result["decision"] == "ACCEPTED"
    assert result["execution"] is not None
    assert result["execution"]["status"] == "COMPLETED"


def test_rejected_route_is_not_executed(coordinator):
    result = coordinator.execute(
        route=valid_route(),
        starting_value=1000.0,
        gross_final_value=1010.0,
        trading_fees=5.0,
        transfer_fees=5.0,
        other_costs=5.0,
        minimum_profit_percent=2.0,
    )

    assert result["accepted"] is False
    assert result["decision"] == "REJECTED"
    assert result["execution"] is None


def test_route_id_is_preserved(coordinator):
    result = coordinator.execute(
        route=valid_route(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=0.0,
        transfer_fees=0.0,
        other_costs=0.0,
        minimum_profit_percent=2.0,
    )

    assert result["route_id"] == "ROUTE-001"


def test_missing_route_is_rejected(coordinator):
    with pytest.raises(ValueError, match="route is required"):
        coordinator.execute(
            route=None,
            starting_value=1000.0,
            gross_final_value=1050.0,
            trading_fees=0.0,
            transfer_fees=0.0,
            other_costs=0.0,
            minimum_profit_percent=2.0,
        )


def test_history_records_result(coordinator):
    coordinator.execute(
        route=valid_route(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=0.0,
        transfer_fees=0.0,
        other_costs=0.0,
        minimum_profit_percent=2.0,
    )

    assert len(coordinator.history()) == 1
