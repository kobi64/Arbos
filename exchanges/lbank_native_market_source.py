"""
ArbOS™
EX-242
LBank Native Market Source

Normalizes LBank public currency-pair metadata into the
standard ArbOS™ native market representation.

Read-only.
No authentication.
No transfers.
No live orders.
"""

import re


class LBankNativeMarketSource:
    LEVERAGED_TOKEN_PATTERN = re.compile(
        r".*(?:3L|3S|5L|5S)$",
        re.IGNORECASE,
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
    def _is_leveraged_token(
        cls,
        base,
    ):
        return (
            cls.LEVERAGED_TOKEN_PATTERN
            .fullmatch(base)
            is not None
        )

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
                "LBank markets unavailable: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise RuntimeError(
                "LBank markets unavailable: "
                "invalid response"
            )

        if (
            payload.get(
                "fetch_complete"
            )
            is not True
        ):
            raise RuntimeError(
                "LBank markets unavailable: "
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
                "LBank markets unavailable: "
                "invalid markets"
            )

        result = []

        for raw_symbol in markets:
            if not isinstance(
                raw_symbol,
                str,
            ):
                continue

            native_symbol = (
                raw_symbol
                .strip()
                .lower()
            )

            if not native_symbol:
                continue

            parts = native_symbol.split(
                "_"
            )

            if len(parts) != 2:
                continue

            base, quote = parts

            if (
                not base
                or not quote
            ):
                continue

            base = base.upper()
            quote = quote.upper()

            if self._is_leveraged_token(
                base
            ):
                continue

            result.append({
                "symbol": (
                    f"{base}/{quote}"
                ),
                "native_symbol": (
                    native_symbol
                ),
                "base": base,
                "quote": quote,
                "active": True,
            })

        return result
