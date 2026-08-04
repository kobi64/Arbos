"""
ArbOS™
EX-086
CCXT Live Market Data Provider
"""


class CCXTLiveMarketDataProvider:
    def __init__(self, exchange):
        self._exchange = exchange
        self._exchange.load_markets()

    def _fetch_ticker(self, symbol):
        if symbol is None or not str(symbol).strip():
            raise ValueError("symbol is required")

        return self._exchange.fetch_ticker(str(symbol).strip())

    def get_price(self, symbol):
        ticker = self._fetch_ticker(symbol)
        price = ticker.get("last")

        if price is None:
            raise ValueError("last price unavailable")

        return float(price)

    def get_bid(self, symbol):
        ticker = self._fetch_ticker(symbol)
        bid = ticker.get("bid")
        if bid is None:
            raise ValueError("bid price unavailable")
        return float(bid)

    def get_ask(self, symbol):
        ticker = self._fetch_ticker(symbol)
        ask = ticker.get("ask")
        if ask is None:
            raise ValueError("ask price unavailable")
        return float(ask)
