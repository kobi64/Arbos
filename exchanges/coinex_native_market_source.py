"""
ArbOS™
EX-231
CoinEx Native Market Source

Retrieves and normalizes CoinEx's native public spot-market catalogue.

Public market data only.
No authentication.
No transfers.
No live orders.
"""


class CoinExNativeMarketSource:
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
                .publicGetSpotMarket()
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
            list,
        ):
            return self._failed_result()

        markets = []

        for raw in data:
            if not isinstance(
                raw,
                dict,
            ):
                continue

            base = str(
                raw.get(
                    "base_ccy",
                    "",
                )
                or ""
            ).strip().upper()

            quote = str(
                raw.get(
                    "quote_ccy",
                    "",
                )
                or ""
            ).strip().upper()

            native_symbol = str(
                raw.get(
                    "market",
                    "",
                )
                or ""
            ).strip().upper()

            if not base or not quote:
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

            api_trading_available = (
                raw.get(
                    "is_api_trading_available"
                )
                is True
            )

            normalized_status = (
                "TRADING"
                if (
                    status == "online"
                    and api_trading_available
                )
                else "SUSPENDED"
            )

            markets.append({
                "symbol": symbol,
                "status": normalized_status,
                "order_types": [
                    "LIMIT",
                    "MARKET",
                ],
                "minimum_amount": raw.get(
                    "min_amount"
                ),
                "minimum_value": None,
                "price_precision": raw.get(
                    "quote_ccy_precision"
                ),
                "amount_precision": raw.get(
                    "base_ccy_precision"
                ),
                "api_trading_available": (
                    api_trading_available
                ),
                "maker_fee_rate": raw.get(
                    "maker_fee_rate"
                ),
                "taker_fee_rate": raw.get(
                    "taker_fee_rate"
                ),
                "native_symbol": (
                    native_symbol
                ),
                "raw": raw,
            })

        return {
            "exchange_id": "coinex",
            "fetch_complete": True,
            "symbols": [
                market[
                    "symbol"
                ]
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
            "exchange_id": "coinex",
            "fetch_complete": False,
            "symbols": [],
            "markets": [],
            "market_count": 0,
            "live_order_submitted": False,
        }
