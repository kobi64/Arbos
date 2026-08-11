"""
ArbOS™
EX-188
Gate Native Market Source

Retrieves and normalizes Gate's native public spot-market catalogue.

Public market data only.
No authentication.
No transfers.
No live orders.
"""


class GateNativeMarketSource:
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
                .publicSpotGetCurrencyPairs()
            )
        except Exception:
            return self._failed_result()

        if not isinstance(response, list):
            return self._failed_result()

        markets = []

        for raw in response:
            if not isinstance(raw, dict):
                continue

            base = str(
                raw.get("base", "")
            ).strip().upper()

            quote = str(
                raw.get("quote", "")
            ).strip().upper()

            raw_id = str(
                raw.get("id", "")
            ).strip().upper()

            if base and quote:
                symbol = f"{base}/{quote}"
            elif "_" in raw_id:
                base, quote = raw_id.split(
                    "_",
                    1,
                )
                symbol = f"{base}/{quote}"
            else:
                continue

            trade_status = str(
                raw.get(
                    "trade_status",
                    "",
                )
            ).strip().lower()

            trading = (
                trade_status == "tradable"
            )

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
                "minimum_amount": raw.get(
                    "min_base_amount"
                ),
                "minimum_value": raw.get(
                    "min_quote_amount"
                ),
                "amount_precision": raw.get(
                    "amount_precision"
                ),
                "price_precision": raw.get(
                    "precision"
                ),
                "raw": raw,
            })

        symbols = [
            market["symbol"]
            for market in markets
        ]

        return {
            "exchange_id": "gate",
            "fetch_complete": True,
            "symbols": symbols,
            "markets": markets,
            "market_count": len(markets),
            "live_order_submitted": False,
        }

    @staticmethod
    def _failed_result():
        return {
            "exchange_id": "gate",
            "fetch_complete": False,
            "symbols": [],
            "markets": [],
            "market_count": 0,
            "live_order_submitted": False,
        }
