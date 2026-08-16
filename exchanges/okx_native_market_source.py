"""
ArbOS™
EX-233
OKX Native Market Source

Normalizes OKX public SPOT instrument metadata into the
standard ArbOS™ native market representation.

Read-only.
No authentication.
No transfers.
No live orders.
"""


class OKXNativeMarketSource:
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
                .fetch_instruments()
            )
        except Exception as exc:
            raise RuntimeError(
                "OKX instruments unavailable: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise RuntimeError(
                "OKX instruments unavailable: "
                "invalid response"
            )

        if payload.get(
            "code"
        ) != "0":
            raise RuntimeError(
                "OKX instruments unavailable: "
                f"{payload.get('msg') or 'exchange error'}"
            )

        data = payload.get(
            "data"
        )

        if not isinstance(
            data,
            list,
        ):
            raise RuntimeError(
                "OKX instruments unavailable: "
                "invalid instrument data"
            )

        markets = []

        for item in data:
            if not isinstance(
                item,
                dict,
            ):
                continue

            if (
                str(
                    item.get(
                        "instType",
                        "",
                    )
                ).strip().upper()
                != "SPOT"
            ):
                continue

            if (
                str(
                    item.get(
                        "state",
                        "",
                    )
                ).strip().lower()
                != "live"
            ):
                continue

            native_symbol = str(
                item.get(
                    "instId",
                    "",
                )
                or ""
            ).strip().upper()

            base = str(
                item.get(
                    "baseCcy",
                    "",
                )
                or ""
            ).strip().upper()

            quote = str(
                item.get(
                    "quoteCcy",
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

            markets.append({
                "symbol": (
                    f"{base}/{quote}"
                ),
                "native_symbol": native_symbol,
                "base": base,
                "quote": quote,
                "active": True,
                "tick_size": item.get(
                    "tickSz"
                ),
                "lot_size": item.get(
                    "lotSz"
                ),
                "min_amount": item.get(
                    "minSz"
                ),
            })

        return markets
