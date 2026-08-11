"""
ArbOS™
EX-188
HTX Native Market Source

Retrieves and normalizes HTX's native public spot-market catalogue.

Public market data only.
No authentication.
No transfers.
No live orders.
"""


class HTXNativeMarketSource:
    def __init__(self, exchange):
        if exchange is None:
            raise ValueError(
                "exchange is required"
            )

        self._exchange = exchange

    def fetch(self):
        try:
            response = (
                self._exchange
                .publicGetCommonSymbols()
            )
        except Exception:
            return self._failed_result()

        if not isinstance(response, dict):
            return self._failed_result()

        data = response.get(
            "data"
        )

        if not isinstance(data, list):
            return self._failed_result()

        markets = []

        for raw in data:
            if not isinstance(raw, dict):
                continue

            base = str(
                raw.get(
                    "base-currency",
                    "",
                )
            ).strip().upper()

            quote = str(
                raw.get(
                    "quote-currency",
                    "",
                )
            ).strip().upper()

            native_symbol = str(
                raw.get(
                    "symbol",
                    "",
                )
            ).strip()

            if not base or not quote:
                continue

            symbol = f"{base}/{quote}"

            state = str(
                raw.get(
                    "state",
                    "",
                )
            ).strip().lower()

            api_trading = str(
                raw.get(
                    "api-trading",
                    "",
                )
            ).strip().lower()

            markets.append({
                "symbol": symbol,
                "status": (
                    "TRADING"
                    if state == "online"
                    else "SUSPENDED"
                ),
                "order_types": [
                    "LIMIT",
                    "MARKET",
                ],
                "minimum_amount": raw.get(
                    "min-order-amt"
                ),
                "minimum_value": raw.get(
                    "min-order-value"
                ),
                "price_precision": raw.get(
                    "price-precision"
                ),
                "amount_precision": raw.get(
                    "amount-precision"
                ),
                "api_trading": api_trading,
                "native_symbol": native_symbol,
                "raw": raw,
            })

        return {
            "exchange_id": "htx",
            "fetch_complete": True,
            "symbols": [
                market["symbol"]
                for market in markets
            ],
            "markets": markets,
            "market_count": len(
                markets
            ),
            "live_order_submitted": False,
        }

    @staticmethod
    def _failed_result():
        return {
            "exchange_id": "htx",
            "fetch_complete": False,
            "symbols": [],
            "markets": [],
            "market_count": 0,
            "live_order_submitted": False,
        }
