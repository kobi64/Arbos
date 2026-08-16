"""
ArbOS™
EX-235
Coinbase Native Market Source

Normalizes Coinbase Exchange public product metadata into the
standard ArbOS™ native market representation.

Read-only.
No authentication.
No transfers.
No live orders.
"""


class CoinbaseNativeMarketSource:
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
                .fetch_products()
            )
        except Exception as exc:
            raise RuntimeError(
                "Coinbase products unavailable: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ) from exc

        if not isinstance(
            payload,
            list,
        ):
            raise RuntimeError(
                "Coinbase products unavailable: "
                "invalid response"
            )

        markets = []

        for item in payload:
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
                ).strip().lower()
                != "online"
            ):
                continue

            if (
                item.get(
                    "trading_disabled"
                )
                is True
            ):
                continue

            native_symbol = str(
                item.get(
                    "id",
                    "",
                )
                or ""
            ).strip().upper()

            base = str(
                item.get(
                    "base_currency",
                    "",
                )
                or ""
            ).strip().upper()

            quote = str(
                item.get(
                    "quote_currency",
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

            base_increment = (
                item.get(
                    "base_increment"
                )
            )

            markets.append({
                "symbol": (
                    f"{base}/{quote}"
                ),
                "native_symbol": native_symbol,
                "base": base,
                "quote": quote,
                "active": True,
                "tick_size": item.get(
                    "quote_increment"
                ),
                "lot_size": (
                    base_increment
                ),
                "min_amount": (
                    base_increment
                ),
            })

        return markets
