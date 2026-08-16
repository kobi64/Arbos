"""
ArbOS™
EX-243
Ourbit Native Market Source

Normalizes Ourbit public exchange-info metadata into the
standard ArbOS™ native market representation.

Read-only.
No authentication.
No transfers.
No live orders.
"""


class OurbitNativeMarketSource:
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
                "Ourbit markets unavailable: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise RuntimeError(
                "Ourbit markets unavailable: "
                "invalid response"
            )

        if (
            payload.get(
                "fetch_complete"
            )
            is not True
        ):
            raise RuntimeError(
                "Ourbit markets unavailable: "
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
                "Ourbit markets unavailable: "
                "invalid markets"
            )

        result = []

        for item in markets:
            if not isinstance(
                item,
                dict,
            ):
                continue

            status = str(
                item.get(
                    "status",
                    "",
                )
                or ""
            ).strip().upper()

            if status != "ENABLED":
                continue

            permissions = item.get(
                "permissions"
            )

            if not isinstance(
                permissions,
                list,
            ):
                continue

            normalized_permissions = {
                str(
                    permission
                    or ""
                ).strip().upper()
                for permission in permissions
            }

            if "SPOT" not in normalized_permissions:
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

            expected_symbol = (
                f"{base}{quote}"
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
