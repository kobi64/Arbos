"""
ArbOS™
EX-236
Kraken Native Market Source

Normalizes Kraken public AssetPairs metadata into the
standard ArbOS™ native market representation.

Read-only.
No authentication.
No transfers.
No live orders.
"""


class KrakenNativeMarketSource:
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
    def _normalize_asset(
        asset,
    ):
        asset = str(
            asset
            or ""
        ).strip().upper()

        aliases = {
            "XBT": "BTC",
            "XXBT": "BTC",
            "XETH": "ETH",
            "ZUSD": "USD",
            "ZEUR": "EUR",
            "ZGBP": "GBP",
            "ZJPY": "JPY",
            "ZCAD": "CAD",
            "ZAUD": "AUD",
        }

        if asset in aliases:
            return aliases[asset]

        if (
            len(asset) > 3
            and asset[0] in {"X", "Z"}
        ):
            stripped = asset[1:]

            if stripped in {
                "BTC",
                "ETH",
                "USD",
                "EUR",
                "GBP",
                "JPY",
                "CAD",
                "AUD",
            }:
                return stripped

        return asset

    @classmethod
    def _canonical_pair(
        cls,
        item,
    ):
        wsname = str(
            item.get(
                "wsname",
                "",
            )
            or ""
        ).strip().upper()

        if "/" in wsname:
            base_raw, quote_raw = (
                wsname.split(
                    "/",
                    1,
                )
            )

            base = cls._normalize_asset(
                base_raw
            )

            quote = cls._normalize_asset(
                quote_raw
            )

            return (
                base,
                quote,
                f"{base}/{quote}",
            )

        base = cls._normalize_asset(
            item.get(
                "base"
            )
        )

        quote = cls._normalize_asset(
            item.get(
                "quote"
            )
        )

        if not base or not quote:
            raise ValueError(
                "missing Kraken pair assets"
            )

        return (
            base,
            quote,
            f"{base}/{quote}",
        )

    def list_markets(
        self,
    ):
        try:
            payload = (
                self._client
                .fetch_asset_pairs()
            )
        except Exception as exc:
            raise RuntimeError(
                "Kraken asset pairs unavailable: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise RuntimeError(
                "Kraken asset pairs unavailable: "
                "invalid response"
            )

        errors = payload.get(
            "error",
            [],
        )

        if errors:
            raise RuntimeError(
                "Kraken asset pairs unavailable: "
                f"{errors}"
            )

        result = payload.get(
            "result"
        )

        if not isinstance(
            result,
            dict,
        ):
            raise RuntimeError(
                "Kraken asset pairs unavailable: "
                "invalid result"
            )

        markets = []

        for item in result.values():
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

            try:
                (
                    base,
                    quote,
                    symbol,
                ) = self._canonical_pair(
                    item
                )
            except Exception:
                continue

            native_symbol = str(
                item.get(
                    "altname",
                    "",
                )
                or ""
            ).strip().upper()

            if not native_symbol:
                continue

            min_amount = item.get(
                "ordermin"
            )

            if min_amount is not None:
                try:
                    min_amount = float(
                        min_amount
                    )
                except Exception:
                    min_amount = None

            markets.append({
                "symbol": symbol,
                "native_symbol": native_symbol,
                "base": base,
                "quote": quote,
                "active": True,
                "price_precision": item.get(
                    "pair_decimals"
                ),
                "amount_precision": item.get(
                    "lot_decimals"
                ),
                "min_amount": min_amount,
            })

        return markets
