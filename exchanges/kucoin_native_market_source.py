"""
ArbOS™
EX-184
KuCoin Native Market Source

Retrieves and normalizes KuCoin's native public spot-market catalogue
for verified native fallback research.

Public market data only.
No authentication.
No transfers.
No live orders.
"""


class KuCoinNativeMarketSource:
    def __init__(self, exchange):
        if exchange is None:
            raise ValueError("exchange is required")

        self._exchange = exchange

    def fetch(self):
        try:
            response = (
                self._exchange.publicGetSymbols()
            )
        except Exception:
            return self._failed_result()

        if not isinstance(response, dict):
            return self._failed_result()

        data = response.get("data")

        if not isinstance(data, list):
            return self._failed_result()

        symbols = []
        markets = []

        for raw in data:
            if not isinstance(raw, dict):
                continue

            native_symbol = str(
                raw.get("symbol", "")
            ).strip().upper()

            base = str(
                raw.get("baseCurrency", "")
            ).strip().upper()

            quote = str(
                raw.get("quoteCurrency", "")
            ).strip().upper()

            if base and quote:
                symbol = f"{base}/{quote}"
            elif "-" in native_symbol:
                base, quote = native_symbol.split(
                    "-",
                    1,
                )
                symbol = f"{base}/{quote}"
            else:
                continue

            trading = (
                raw.get("enableTrading")
                is True
            )

            symbols.append(symbol)

            markets.append({
                "symbol": symbol,
                "status": (
                    "TRADING"
                    if trading
                    else "SUSPENDED"
                ),
                "order_types": [
                    "LIMIT",
                    "MARKET",
                ],
                "raw": raw,
            })

        return {
            "fetch_complete": True,
            "symbols": symbols,
            "markets": markets,
        }

    @staticmethod
    def _failed_result():
        return {
            "fetch_complete": False,
            "symbols": [],
            "markets": [],
        }
