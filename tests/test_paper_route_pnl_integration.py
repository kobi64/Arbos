import pytest

from exchanges.paper_route_pnl_integration import (
    PaperRoutePnLIntegration,
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
def integration():
    return PaperRoutePnLIntegration(FakeMarketDataProvider())


def valid_route():
    return {
        "route_id": "ROUTE-001",
        "legs": [
            {"symbol": "BTC/USDT", "side": "buy", "quantity": 0.01},
            {"symbol": "ETH/BTC", "side": "buy", "quantity": 0.2},
            {"symbol": "ETH/USDT", "side": "sell", "quantity": 0.2},
        ],
    }


def test_route_execution_and_pnl_are_returned_together(integration):
    result = integration.execute(
        route=valid_route(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    assert result["execution"]["status"] == "COMPLETED"
    assert result["pnl"]["net_profit"] == 40.0


def test_route_id_is_preserved(integration):
    result = integration.execute(
        route=valid_route(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    assert result["route_id"] == "ROUTE-001"


def test_profitable_flag_is_returned(integration):
    result = integration.execute(
        route=valid_route(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    assert result["pnl"]["profitable"] is True


def test_unprofitable_after_costs_is_reported(integration):
    result = integration.execute(
        route=valid_route(),
        starting_value=1000.0,
        gross_final_value=1030.0,
        trading_fees=15.0,
        transfer_fees=10.0,
        other_costs=5.0,
        minimum_profit_percent=2.0,
    )

    assert result["pnl"]["profitable"] is False
    assert result["pnl"]["net_profit"] == 0.0


def test_all_route_legs_are_returned(integration):
    result = integration.execute(
        route=valid_route(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    assert len(result["execution"]["legs"]) == 3


def test_missing_route_is_rejected(integration):
    with pytest.raises(ValueError, match="route is required"):
        integration.execute(
            route=None,
            starting_value=1000.0,
            gross_final_value=1050.0,
            trading_fees=0.0,
            transfer_fees=0.0,
            other_costs=0.0,
            minimum_profit_percent=2.0,
        )


def test_history_records_integrated_result(integration):
    integration.execute(
        route=valid_route(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    assert len(integration.history()) == 1


def test_history_preserves_route_and_pnl(integration):
    integration.execute(
        route=valid_route(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    record = integration.history()[0]
    assert record["route_id"] == "ROUTE-001"
    assert record["pnl"]["net_profit"] == 40.0


def test_history_preserves_route_and_pnl(integration):
    integration.execute(
        route=valid_route(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    record = integration.history()[0]
    assert record["route_id"] == "ROUTE-001"
    assert record["pnl"]["net_profit"] == 40.0
