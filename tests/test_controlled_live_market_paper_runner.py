import pytest

from core.controlled_live_market_paper_runner import (
    ControlledLiveMarketPaperRunner,
)


class FakeExchange:
    def __init__(self):
        self.markets_loaded = False

    def load_markets(self):
        self.markets_loaded = True
        return {}

    def fetch_ticker(self, symbol):
        prices = {
            "BTC/USDT": {"last": 62000.0, "bid": 61900.0, "ask": 62000.0},
            "ETH/BTC": {"last": 0.0495, "bid": 0.049, "ask": 0.05},
            "ETH/USDT": {"last": 3205.0, "bid": 3200.0, "ask": 3210.0},
        }
        return prices[symbol]


def valid_opportunity():
    return {
        "opportunity_id": "LIVE-PAPER-001",
        "legs": [
            {"symbol": "BTC/USDT", "side": "buy"},
            {"symbol": "ETH/BTC", "side": "buy"},
            {"symbol": "ETH/USDT", "side": "sell"},
        ],
    }


def test_runs_live_market_paper_trade_without_live_order():
    runner = ControlledLiveMarketPaperRunner(FakeExchange())

    result = runner.run(
        opportunity=valid_opportunity(),
        starting_value=1000.0,
        trading_fees=0.0,
        transfer_fees=0.0,
        other_costs=0.0,
        minimum_profit_percent=0.0,
    )

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False
    assert result["decision"] in {"ACCEPTED", "REJECTED"}
    assert "valuation" in result


def test_loads_exchange_markets():
    exchange = FakeExchange()
    ControlledLiveMarketPaperRunner(exchange)

    assert exchange.markets_loaded is True


def test_missing_opportunity_is_rejected():
    runner = ControlledLiveMarketPaperRunner(FakeExchange())

    with pytest.raises(ValueError, match="opportunity is required"):
        runner.run(
            opportunity=None,
            starting_value=1000.0,
            trading_fees=0.0,
            transfer_fees=0.0,
            other_costs=0.0,
            minimum_profit_percent=0.0,
        )
