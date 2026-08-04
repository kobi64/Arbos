import pytest

from exchanges.ccxt_live_market_data_provider import (
    CCXTLiveMarketDataProvider,
)


class FakeExchange:
    def __init__(self):
        self.markets_loaded = False

    def load_markets(self):
        self.markets_loaded = True
        return {"BTC/USDT": {}}

    def fetch_ticker(self, symbol):
        return {"last": 62000.0, "bid": 61990.0, "ask": 62010.0}


def test_loads_markets_on_creation():
    exchange = FakeExchange()
    CCXTLiveMarketDataProvider(exchange)

    assert exchange.markets_loaded is True


def test_get_price_returns_last_price():
    provider = CCXTLiveMarketDataProvider(FakeExchange())

    assert provider.get_price("BTC/USDT") == 62000.0


def test_get_bid_returns_bid_price():
    provider = CCXTLiveMarketDataProvider(FakeExchange())

    assert provider.get_bid("BTC/USDT") == 61990.0


def test_get_ask_returns_ask_price():
    provider = CCXTLiveMarketDataProvider(FakeExchange())

    assert provider.get_ask("BTC/USDT") == 62010.0


class MissingPriceExchange(FakeExchange):
    def fetch_ticker(self, symbol):
        return {"last": None, "bid": None, "ask": None}


def test_missing_last_price_is_rejected():
    provider = CCXTLiveMarketDataProvider(MissingPriceExchange())

    with pytest.raises(ValueError, match="last price unavailable"):
        provider.get_price("BTC/USDT")


def test_missing_symbol_is_rejected():
    provider = CCXTLiveMarketDataProvider(FakeExchange())

    with pytest.raises(ValueError, match="symbol is required"):
        provider.get_price("")
