"""
ArbOS™
EX-182
Verified Native Order Book Provider

Exchange-agnostic policy layer for public market-data fallback.

Normal market data is always preferred.

If the normalized provider cannot supply the requested market,
native public depth may be used only when an independent verified
market source confirms that the symbol is trusted for research.

Public market data / paper valuation only.
No authentication.
No transfers.
No live orders.
"""


class VerifiedNativeOrderBookProvider:
    def __init__(
        self,
        exchange_id,
        normal_provider,
        native_provider,
        verified_market_source,
    ):
        if exchange_id is None or not str(exchange_id).strip():
            raise ValueError("exchange_id is required")

        if normal_provider is None:
            raise ValueError("normal_provider is required")

        if native_provider is None:
            raise ValueError("native_provider is required")

        if verified_market_source is None:
            raise ValueError(
                "verified_market_source is required"
            )

        self._exchange_id = str(
            exchange_id
        ).strip().lower()

        self._normal_provider = normal_provider
        self._native_provider = native_provider
        self._verified_market_source = (
            verified_market_source
        )

    def snapshot(
        self,
        symbol,
        limit=None,
    ):
        if symbol is None or not str(symbol).strip():
            raise ValueError("symbol is required")

        symbol = str(
            symbol
        ).strip().upper()

        try:
            normal = self._normal_provider.snapshot(
                symbol,
                limit=limit,
            )

            return {
                **normal,
                "symbol": symbol,
                "market_source": (
                    "CCXT_NORMALIZED"
                ),
            }

        except Exception as normal_error:
            if not self._is_verified(
                symbol
            ):
                raise normal_error

        native = self._native_provider.snapshot(
            symbol,
            limit=limit,
        )

        return {
            **native,
            "symbol": symbol,
            "market_source": (
                "VERIFIED_RAW_ONLY_"
                f"{self._exchange_id.upper()}_NATIVE"
            ),
            "market_verified": True,
            "paper_only": True,
            "live_order_submitted": False,
        }

    def _is_verified(self, symbol):
        method = getattr(
            self._verified_market_source,
            "is_verified",
            None,
        )

        if not callable(method):
            raise ValueError(
                "verified market source must "
                "provide is_verified"
            )

        return bool(
            method(symbol)
        )
