"""
ArbOS™
EX-232
Phemex Native Market Source

Retrieves and normalizes Phemex's native public spot-market
catalogue.

Important:
- only products with type == "Spot" are exposed
- perpetual products are excluded from the spot universe
- Phemex spot native symbols use the s-prefix, e.g. sBTCUSDT

Public market data only.
No authentication.
No transfers.
No live orders.
"""


class PhemexNativeMarketSource:
    def __init__(
        self,
        exchange,
    ):
        if exchange is None:
            raise ValueError(
                "exchange is required"
            )

        self._exchange = exchange

    def fetch(
        self,
    ):
        try:
            response = (
                self._exchange
                .publicGetProducts()
            )
        except Exception:
            return self._failed_result()

        if not isinstance(
            response,
            dict,
        ):
            return self._failed_result()

        if response.get(
            "code"
        ) != 0:
            return self._failed_result()

        data = response.get(
            "data"
        )

        if not isinstance(
            data,
            dict,
        ):
            return self._failed_result()

        products = data.get(
            "products"
        )

        if not isinstance(
            products,
            list,
        ):
            return self._failed_result()

        markets = []

        for raw in products:
            if not isinstance(
                raw,
                dict,
            ):
                continue

            product_type = str(
                raw.get(
                    "type",
                    "",
                )
                or ""
            ).strip()

            if product_type != "Spot":
                continue

            base = str(
                raw.get(
                    "baseCurrency",
                    "",
                )
                or ""
            ).strip().upper()

            quote = str(
                raw.get(
                    "quoteCurrency",
                    "",
                )
                or ""
            ).strip().upper()

            native_symbol = str(
                raw.get(
                    "symbol",
                    "",
                )
                or ""
            ).strip()

            if (
                not base
                or not quote
                or not native_symbol
            ):
                continue

            symbol = (
                f"{base}/{quote}"
            )

            status = str(
                raw.get(
                    "status",
                    "",
                )
                or ""
            ).strip().lower()

            normalized_status = (
                "TRADING"
                if status == "listed"
                else "SUSPENDED"
            )

            markets.append({
                "symbol": symbol,
                "status": normalized_status,
                "order_types": [
                    "LIMIT",
                    "MARKET",
                ],
                "minimum_amount": None,
                "minimum_value": raw.get(
                    "minOrderValue"
                ),
                "price_scale": raw.get(
                    "priceScale"
                ),
                "price_precision": raw.get(
                    "pricePrecision"
                ),
                "amount_precision": raw.get(
                    "baseQtyPrecision"
                ),
                "maker_fee_rate": raw.get(
                    "defaultMakerFee"
                ),
                "taker_fee_rate": raw.get(
                    "defaultTakerFee"
                ),
                "native_symbol": native_symbol,
                "product_type": product_type,
                "raw": raw,
            })

        return {
            "exchange_id": "phemex",
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
            "exchange_id": "phemex",
            "fetch_complete": False,
            "symbols": [],
            "markets": [],
            "market_count": 0,
            "live_order_submitted": False,
        }
