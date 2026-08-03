import pytest

from exchanges.paper_route_decision_coordinator import (
    PaperRouteDecisionCoordinator,
)


class FakeMarketDataProvider:
    def __init__(self, prices=None):
        self.prices = prices or {
            "BTC/USDT": 62000.0,
            "ETH/BTC": 0.05,
            "ETH/USDT": 3200.0,
        }

    def get_price(self, symbol):
        return self.prices.get(symbol)


@pytest.fixture
def coordinator():
    return PaperRouteDecisionCoordinator(FakeMarketDataProvider())


def valid_route():
    return {
        "route_id": "ROUTE-001",
        "legs": [
            {"symbol": "BTC/USDT", "side": "buy", "quantity": 0.01},
            {"symbol": "ETH/BTC", "side": "buy", "quantity": 0.2},
            {"symbol": "ETH/USDT", "side": "sell", "quantity": 0.2},
        ],
    }


def test_profitable_route_is_accepted(coordinator):
    result = coordinator.execute(
        route=valid_route(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    assert result["decision"] == "ACCEPTED"
    assert result["accepted"] is True


def test_unprofitable_route_is_rejected(coordinator):
    result = coordinator.execute(
        route=valid_route(),
        starting_value=1000.0,
        gross_final_value=1030.0,
        trading_fees=15.0,
        transfer_fees=10.0,
        other_costs=5.0,
        minimum_profit_percent=2.0,
    )

    assert result["decision"] == "REJECTED"
    assert result["accepted"] is False


def test_route_id_is_preserved(coordinator):
    result = coordinator.execute(
        route=valid_route(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    assert result["route_id"] == "ROUTE-001"


def test_pnl_is_preserved(coordinator):
    result = coordinator.execute(
        route=valid_route(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    assert result["pnl"]["net_profit"] == 40.0
    assert result["pnl"]["profit_percent"] == 4.0


def test_execution_result_is_preserved(coordinator):
    result = coordinator.execute(
        route=valid_route(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    assert result["execution"]["status"] == "COMPLETED"
    assert len(result["execution"]["legs"]) == 3


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


def test_history_records_decision(coordinator):
    coordinator.execute(
        route=valid_route(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    assert len(coordinator.history()) == 1
