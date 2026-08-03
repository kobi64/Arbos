import pytest

from exchanges.live_paper_decision_pipeline import (
    LivePaperDecisionPipeline,
)


class FakeLiveMarketDataProvider:
    def __init__(self, prices=None):
        self.prices = prices or {
            "BTC/USDT": 62000.0,
            "ETH/BTC": 0.05,
            "ETH/USDT": 3200.0,
        }

    def get_price(self, symbol):
        return self.prices.get(symbol)


@pytest.fixture
def pipeline():
    return LivePaperDecisionPipeline(FakeLiveMarketDataProvider())


def valid_opportunity():
    return {
        "opportunity_id": "OPP-001",
        "legs": [
            {"symbol": "BTC/USDT", "side": "buy", "quantity": 0.01},
            {"symbol": "ETH/BTC", "side": "buy", "quantity": 0.2},
            {"symbol": "ETH/USDT", "side": "sell", "quantity": 0.2},
        ],
    }


def test_profitable_live_opportunity_is_accepted(pipeline):
    result = pipeline.execute(
        opportunity=valid_opportunity(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    assert result["decision"] == "ACCEPTED"
    assert result["accepted"] is True


def test_opportunity_id_becomes_route_id(pipeline):
    result = pipeline.execute(
        opportunity=valid_opportunity(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    assert result["route_id"] == "OPP-001"


def test_live_market_prices_are_preserved(pipeline):
    result = pipeline.execute(
        opportunity=valid_opportunity(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    legs = result["execution"]["legs"]
    assert legs[0]["average_price"] == 62000.0
    assert legs[1]["average_price"] == 0.05
    assert legs[2]["average_price"] == 3200.0


def test_unprofitable_live_opportunity_is_rejected(pipeline):
    result = pipeline.execute(
        opportunity=valid_opportunity(),
        starting_value=1000.0,
        gross_final_value=1030.0,
        trading_fees=15.0,
        transfer_fees=10.0,
        other_costs=5.0,
        minimum_profit_percent=2.0,
    )

    assert result["decision"] == "REJECTED"
    assert result["accepted"] is False


def test_missing_opportunity_is_rejected(pipeline):
    with pytest.raises(ValueError, match="opportunity is required"):
        pipeline.execute(
            opportunity=None,
            starting_value=1000.0,
            gross_final_value=1050.0,
            trading_fees=0.0,
            transfer_fees=0.0,
            other_costs=0.0,
            minimum_profit_percent=2.0,
        )


def test_history_records_decision(pipeline):
    pipeline.execute(
        opportunity=valid_opportunity(),
        starting_value=1000.0,
        gross_final_value=1050.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    assert len(pipeline.history()) == 1
