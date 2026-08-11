"""
ArbOS™
EX-188
Bitget Native Market Source

Retrieves and normalizes Bitget's native public spot-market catalogue.

Public market data only.
No authentication.
No transfers.
No live orders.
"""


class BitgetNativeMarketSource:
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
                .publicSpotGetV2SpotPublicSymbols()
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
                    "baseCoin",
                    "",
                )
            ).strip().upper()

            quote = str(
                raw.get(
                    "quoteCoin",
                    "",
                )
            ).strip().upper()

            native_symbol = str(
                raw.get(
                    "symbol",
                    "",
                )
            ).strip().upper()

            if base and quote:
                symbol = f"{base}/{quote}"
            else:
                continue

            status = str(
                raw.get(
                    "status",
                    "",
                )
            ).strip().lower()

            markets.append({
                "symbol": symbol,
                "status": (
                    "TRADING"
                    if status == "online"
                    else "SUSPENDED"
                ),
                "order_types": [
                    "LIMIT",
                    "MARKET",
                ],
                "minimum_amount": raw.get(
                    "minTradeAmount"
                ),
                "minimum_value": raw.get(
                    "minTradeUSDT"
                ),
                "price_precision": raw.get(
                    "pricePrecision"
                ),
                "amount_precision": raw.get(
                    "quantityPrecision"
                ),
                "raw": raw,
                "native_symbol": (
                    native_symbol
                ),
            })

        return {
            "exchange_id": "bitget",
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
            "exchange_id": "bitget",
            "fetch_complete": False,
            "symbols": [],
            "markets": [],
            "market_count": 0,
            "live_order_submitted": False,
        }
