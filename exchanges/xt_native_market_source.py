"""
ArbOS™
EX-188
XT Native Market Source

Retrieves and normalizes XT's native public spot-market catalogue.

Public market data only.
No authentication.
No transfers.
No live orders.
"""


class XTNativeMarketSource:
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
                .publicSpotGetSymbol()
            )
        except Exception:
            return self._failed_result()

        if not isinstance(response, dict):
            return self._failed_result()

        result = response.get(
            "result"
        )

        if not isinstance(result, dict):
            return self._failed_result()

        symbols_data = result.get(
            "symbols"
        )

        if not isinstance(symbols_data, list):
            return self._failed_result()

        markets = []

        for raw in symbols_data:
            if not isinstance(raw, dict):
                continue

            base = str(
                raw.get(
                    "baseCurrency",
                    "",
                )
            ).strip().upper()

            quote = str(
                raw.get(
                    "quoteCurrency",
                    "",
                )
            ).strip().upper()

            if not base or not quote:
                continue

            symbol = f"{base}/{quote}"

            state = str(
                raw.get(
                    "state",
                    "",
                )
            ).strip().upper()

            trading = (
                state == "ONLINE"
                and raw.get(
                    "tradingEnabled"
                ) is True
                and raw.get(
                    "openapiEnabled"
                ) is True
            )

            minimum_value = None

            filters = raw.get(
                "filters",
                [],
            )

            if isinstance(filters, list):
                for item in filters:
                    if not isinstance(
                        item,
                        dict,
                    ):
                        continue

                    if (
                        str(
                            item.get(
                                "filter",
                                "",
                            )
                        ).strip().upper()
                        == "QUOTE_QTY"
                    ):
                        minimum_value = (
                            item.get("min")
                        )
                        break

            order_types = raw.get(
                "orderTypes"
            )

            if not isinstance(
                order_types,
                list,
            ):
                order_types = []

            markets.append({
                "symbol": symbol,
                "status": (
                    "TRADING"
                    if trading
                    else "SUSPENDED"
                ),
                "order_types": order_types,
                "minimum_value": (
                    minimum_value
                ),
                "price_precision": raw.get(
                    "pricePrecision"
                ),
                "amount_precision": raw.get(
                    "quantityPrecision"
                ),
                "native_market_id": raw.get(
                    "id"
                ),
                "native_symbol": raw.get(
                    "symbol"
                ),
                "trading_enabled": raw.get(
                    "tradingEnabled"
                ),
                "openapi_enabled": raw.get(
                    "openapiEnabled"
                ),
                "raw": raw,
            })

        return {
            "exchange_id": "xt",
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
            "exchange_id": "xt",
            "fetch_complete": False,
            "symbols": [],
            "markets": [],
            "market_count": 0,
            "live_order_submitted": False,
        }
