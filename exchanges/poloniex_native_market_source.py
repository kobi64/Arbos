"""
ArbOS™
EX-241
Poloniex Native Market Source

Normalizes Poloniex public market metadata into the
standard ArbOS™ native market representation.

Read-only.
No authentication.
No transfers.
No live orders.
"""


class PoloniexNativeMarketSource:
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
                .fetch_markets()
            )
        except Exception as exc:
            raise RuntimeError(
                "Poloniex markets unavailable: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise RuntimeError(
                "Poloniex markets unavailable: "
                "invalid response"
            )

        if (
            payload.get(
                "fetch_complete"
            )
            is not True
        ):
            raise RuntimeError(
                "Poloniex markets unavailable: "
                f"{payload.get('reason', 'unknown')}"
            )

        markets = payload.get(
            "markets"
        )

        if not isinstance(
            markets,
            list,
        ):
            raise RuntimeError(
                "Poloniex markets unavailable: "
                "invalid markets"
            )

        result = []

        for item in markets:
            if not isinstance(
                item,
                dict,
            ):
                continue

            state = str(
                item.get(
                    "state",
                    "",
                )
                or ""
            ).strip().upper()

            if state != "NORMAL":
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
                    "baseCurrencyName",
                    "",
                )
                or ""
            ).strip().upper()

            quote = str(
                item.get(
                    "quoteCurrencyName",
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

            expected_symbol = (
                f"{base}_{quote}"
            )

            if (
                native_symbol
                != expected_symbol
            ):
                continue

            result.append({
                "symbol": (
                    f"{base}/{quote}"
                ),
                "native_symbol": native_symbol,
                "base": base,
                "quote": quote,
                "active": True,
            })

        return result
