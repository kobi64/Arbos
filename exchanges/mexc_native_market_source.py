"""
ArbOS™
EX-238
MEXC Native Market Source

Normalizes MEXC public exchange-info metadata into the
standard ArbOS™ native market representation.

Read-only.
No authentication.
No transfers.
No live orders.
"""


class MexcNativeMarketSource:
    def __init__(
        self,
        client,
    ):
        if client is None:
            raise ValueError(
                "client is required"
            )

        self._client = client

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
                "MEXC exchange info unavailable: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise RuntimeError(
                "MEXC exchange info unavailable: "
                "invalid response"
            )

        if (
            payload.get(
                "fetch_complete"
            )
            is not True
        ):
            raise RuntimeError(
                "MEXC exchange info unavailable: "
                f"{payload.get('reason', 'unknown')}"
            )

        symbols = payload.get(
            "symbols"
        )

        if not isinstance(
            symbols,
            list,
        ):
            raise RuntimeError(
                "MEXC exchange info unavailable: "
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
                ).strip()
                != "1"
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

            min_amount = item.get(
                "baseSizePrecision"
            )

            if min_amount is not None:
                try:
                    min_amount = float(
                        min_amount
                    )
                except Exception:
                    min_amount = None

            order_types = item.get(
                "orderTypes",
                [],
            )

            if not isinstance(
                order_types,
                list,
            ):
                order_types = []

            markets.append({
                "symbol": f"{base}/{quote}",
                "native_symbol": native_symbol,
                "base": base,
                "quote": quote,
                "active": True,
                "amount_precision": (
                    item.get(
                        "baseAssetPrecision"
                    )
                ),
                "price_precision": (
                    item.get(
                        "quoteAssetPrecision"
                    )
                ),
                "min_amount": min_amount,
                "order_types": order_types,
            })

        return markets
