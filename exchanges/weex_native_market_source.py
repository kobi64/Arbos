"""
ArbOS™
EX-240
WEEX Native Market Source

Normalizes WEEX public trading-symbol metadata into the
standard ArbOS™ native market representation.

Read-only.
No authentication.
No transfers.
No live orders.
"""


class WeexNativeMarketSource:
    QUOTE_ASSETS = (
        "USDT",
        "USDC",
        "FDUSD",
        "TUSD",
        "DAI",
        "BTC",
        "ETH",
        "EUR",
        "USD",
    )

    def __init__(
        self,
        client,
    ):
        if client is None:
            raise ValueError(
                "client is required"
            )

        self._client = client

    @classmethod
    def _split_symbol(
        cls,
        native_symbol,
    ):
        native_symbol = str(
            native_symbol
            or ""
        ).strip().upper()

        if not native_symbol:
            return None

        for quote in sorted(
            cls.QUOTE_ASSETS,
            key=len,
            reverse=True,
        ):
            if not native_symbol.endswith(
                quote
            ):
                continue

            base = native_symbol[
                : -len(quote)
            ]

            if not base:
                continue

            return (
                base,
                quote,
            )

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
                "WEEX symbols unavailable: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise RuntimeError(
                "WEEX symbols unavailable: "
                "invalid response"
            )

        if (
            payload.get(
                "fetch_complete"
            )
            is not True
        ):
            raise RuntimeError(
                "WEEX symbols unavailable: "
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
                "WEEX symbols unavailable: "
                "invalid symbols"
            )

        markets = []

        for raw_symbol in symbols:
            native_symbol = str(
                raw_symbol
                or ""
            ).strip().upper()

            split = self._split_symbol(
                native_symbol
            )

            if split is None:
                continue

            base, quote = split

            markets.append({
                "symbol": f"{base}/{quote}",
                "native_symbol": native_symbol,
                "base": base,
                "quote": quote,
                "active": True,
            })

        return markets
