"""
ArbOS™
EX-239
BingX Native Market Source

Normalizes BingX public symbol metadata into the
standard ArbOS™ native market representation.

Read-only.
No authentication.
No transfers.
No live orders.
"""


class BingXNativeMarketSource:
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
    def _to_float(
        value,
    ):
        if value is None:
            return None

        try:
            return float(
                value
            )
        except (
            TypeError,
            ValueError,
        ):
            return None

    def list_markets(
        self,
    ):
        try:
            payload = (
                self._client
                .fetch_symbols()
            )
        except Exception as exc:
            raise RuntimeError(
                "BingX symbols unavailable: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise RuntimeError(
                "BingX symbols unavailable: "
                "invalid response"
            )

        if (
            payload.get(
                "fetch_complete"
            )
            is not True
        ):
            raise RuntimeError(
                "BingX symbols unavailable: "
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
                "BingX symbols unavailable: "
                "invalid symbols"
            )

        markets = []

        for item in symbols:
            if not isinstance(
                item,
                dict,
            ):
                continue

            status = item.get(
                "status"
            )

            if str(
                status
            ).strip() not in {
                "1",
                "true",
                "True",
            }:
                continue

            native_symbol = str(
                item.get(
                    "symbol",
                    "",
                )
                or ""
            ).strip().upper()

            if "-" not in native_symbol:
                continue

            base, quote = (
                native_symbol.split(
                    "-",
                    1,
                )
            )

            base = base.strip()
            quote = quote.strip()

            if (
                not base
                or not quote
            ):
                continue

            markets.append({
                "symbol": f"{base}/{quote}",
                "native_symbol": native_symbol,
                "base": base,
                "quote": quote,
                "active": True,
                "min_amount": self._to_float(
                    item.get(
                        "minQty"
                    )
                ),
                "min_notional": self._to_float(
                    item.get(
                        "minNotional"
                    )
                ),
                "tick_size": self._to_float(
                    item.get(
                        "tickSize"
                    )
                ),
                "step_size": self._to_float(
                    item.get(
                        "stepSize"
                    )
                ),
            })

        return markets
