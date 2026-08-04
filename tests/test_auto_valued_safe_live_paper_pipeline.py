import pytest

from exchanges.auto_valued_safe_live_paper_pipeline import (
    AutoValuedSafeLivePaperPipeline,
)


class FakeMarketDataProvider:
    def __init__(self):
        self.prices = {
            "BTC/USDT": {"bid": 61900.0, "ask": 62000.0},
            "ETH/BTC": {"bid": 0.049, "ask": 0.05},
            "ETH/USDT": {"bid": 3200.0, "ask": 3210.0},
        }

    def get_price(self, symbol):
        data = self.prices[symbol]
        return (data["bid"] + data["ask"]) / 2.0

    def get_bid(self, symbol):
        return self.prices[symbol]["bid"]

    def get_ask(self, symbol):
        return self.prices[symbol]["ask"]


@pytest.fixture
def pipeline():
    return AutoValuedSafeLivePaperPipeline(FakeMarketDataProvider())


def valid_opportunity():
    return {
        "opportunity_id": "OPP-001",
        "legs": [
            {"symbol": "BTC/USDT", "side": "buy"},
            {"symbol": "ETH/BTC", "side": "buy"},
            {"symbol": "ETH/USDT", "side": "sell"},
        ],
    }


def test_pipeline_calculates_gross_final_value_automatically(pipeline):
    result = pipeline.execute(
        opportunity=valid_opportunity(),
        starting_value=1000.0,
        trading_fees=0.0,
        transfer_fees=0.0,
        other_costs=0.0,
        minimum_profit_percent=0.0,
    )

    expected = ((1000.0 / 62000.0) / 0.05) * 3200.0
    assert result["valuation"]["gross_final_value"] == pytest.approx(expected)


def test_auto_valued_result_feeds_pnl(pipeline):
    result = pipeline.execute(
        opportunity=valid_opportunity(),
        starting_value=1000.0,
        trading_fees=0.0,
        transfer_fees=0.0,
        other_costs=0.0,
        minimum_profit_percent=0.0,
    )

    assert result["pnl"]["net_profit"] == pytest.approx(
        result["valuation"]["gross_final_value"] - 1000.0
    )


def test_missing_opportunity_is_rejected(pipeline):
    with pytest.raises(ValueError, match="opportunity is required"):
        pipeline.execute(
            opportunity=None,
            starting_value=1000.0,
            trading_fees=0.0,
            transfer_fees=0.0,
            other_costs=0.0,
            minimum_profit_percent=0.0,
        )


def test_pipeline_returns_final_decision(pipeline):
    result = pipeline.execute(
        opportunity=valid_opportunity(),
        starting_value=1000.0,
        trading_fees=0.0,
        transfer_fees=0.0,
        other_costs=0.0,
        minimum_profit_percent=0.0,
    )

    assert result["decision"] in {"ACCEPTED", "REJECTED"}
