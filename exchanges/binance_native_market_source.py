"""
ArbOS™
EX-234
Binance Native Market Source

Normalizes Binance public SPOT exchange information into the
standard ArbOS™ native market representation.

Read-only.
No authentication.
No transfers.
No live orders.
"""


class BinanceNativeMarketSource:
    def __init__(
        self,
        client,
    ):
        if client is None:
            raise ValueError(
                "client is required"
            )

        self._client = client

    @staticmethod
    def _find_filter(
        filters,
        filter_type,
    ):
        if not isinstance(
            filters,
            list,
        ):
            return {}

        for item in filters:
            if (
                isinstance(item, dict)
                and item.get(
                    "filterType"
                ) == filter_type
            ):
                return item

        return {}

    def list_markets(
        self,
    ):
        try:
            payload = (
                self._client
                .fetch_exchange_info()
            )
        except Exception as exc:
            raise RuntimeError(
                "Binance exchange info unavailable: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise RuntimeError(
                "Binance exchange info unavailable: "
                "invalid response"
            )

        symbols = payload.get(
            "symbols"
        )

        if not isinstance(
            symbols,
            list,
        ):
            raise RuntimeError(
                "Binance exchange info unavailable: "
                "invalid symbols"
            )

        markets = []

        for item in symbols:
            if not isinstance(
                item,
                dict,
            ):
                continue

            if (
                str(
                    item.get(
                        "status",
                        "",
                    )
                ).strip().upper()
                != "TRADING"
            ):
                continue

            if (
                item.get(
                    "isSpotTradingAllowed"
                )
                is not True
            ):
                continue

            native_symbol = str(
                item.get(
                    "symbol",
                    "",
                )
                or ""
            ).strip().upper()

            base = str(
                item.get(
                    "baseAsset",
                    "",
                )
                or ""
            ).strip().upper()

            quote = str(
                item.get(
                    "quoteAsset",
                    "",
                )
                or ""
            ).strip().upper()

            if (
                not native_symbol
                or not base
                or not quote
            ):
                continue

            filters = item.get(
                "filters",
                [],
            )

            price_filter = (
                self._find_filter(
                    filters,
                    "PRICE_FILTER",
                )
            )

            lot_filter = (
                self._find_filter(
                    filters,
                    "LOT_SIZE",
                )
            )

            markets.append({
                "symbol": (
                    f"{base}/{quote}"
                ),
                "native_symbol": (
                    native_symbol
                ),
                "base": base,
                "quote": quote,
                "active": True,
                "tick_size": (
                    price_filter.get(
                        "tickSize"
                    )
                ),
                "lot_size": (
                    lot_filter.get(
                        "stepSize"
                    )
                ),
                "min_amount": (
                    lot_filter.get(
                        "minQty"
                    )
                ),
            })

        return markets
