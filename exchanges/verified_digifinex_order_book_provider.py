"""
ArbOS™
EX-181
Verified DigiFinex Order Book Provider

Uses normal CCXT order-book data when available.

If a DigiFinex market is missing from CCXT's normalized catalogue,
a native public order book is permitted only when EX-176 verifies
that the RAW_ONLY market exists and is actively tradable.

Public market data / paper valuation only.
No authentication.
No transfers.
No live orders.
"""

from exchanges.digifinex_native_market_source import (
    DigiFinexNativeMarketSource,
)
from exchanges.digifinex_native_order_book_source import (
    DigiFinexNativeOrderBookSource,
)
from exchanges.exchange_market_completeness_validator import (
    ExchangeMarketCompletenessValidator,
)
from exchanges.live_order_book_snapshot_engine import (
    LiveOrderBookSnapshotEngine,
)
from exchanges.verified_exchange_market_registry import (
    VerifiedExchangeMarketRegistry,
)


class VerifiedDigiFinexOrderBookProvider:
    def __init__(self, exchange):
        if exchange is None:
            raise ValueError("exchange is required")

        self._exchange = exchange
        self._normal = LiveOrderBookSnapshotEngine(
            exchange
        )
        self._native = DigiFinexNativeOrderBookSource(
            exchange
        )

        self._verified_raw_only = None

    def snapshot(self, symbol, limit=None):
        if symbol is None or not str(symbol).strip():
            raise ValueError("symbol is required")

        symbol = str(symbol).strip().upper()

        try:
            result = self._normal.snapshot(
                symbol,
                limit=limit,
            )

            return {
                **result,
                "market_source": "CCXT_NORMALIZED",
            }

        except Exception as normal_error:
            if not self._is_verified_raw_only(
                symbol
            ):
                raise normal_error

        result = self._native.snapshot(
            symbol,
            limit=limit,
        )

        return {
            **result,
            "market_source": (
                "VERIFIED_RAW_ONLY_DIGIFINEX_NATIVE"
            ),
            "market_verified": True,
            "paper_only": True,
            "live_order_submitted": False,
        }

    def _is_verified_raw_only(self, symbol):
        if self._verified_raw_only is None:
            self._build_registry()

        return symbol in self._verified_raw_only

    def _build_registry(self):
        markets = self._exchange.load_markets()

        ccxt_symbols = list(
            (markets or {}).keys()
        )

        native_result = (
            DigiFinexNativeMarketSource(
                self._exchange
            ).fetch()
        )

        if (
            native_result.get(
                "fetch_complete"
            )
            is not True
        ):
            self._verified_raw_only = set()
            return

        comparison = (
            ExchangeMarketCompletenessValidator()
            .validate(
                exchange_id="digifinex",
                ccxt_symbols=ccxt_symbols,
                raw_symbols=native_result.get(
                    "symbols",
                    [],
                ),
            )
        )

        registry = (
            VerifiedExchangeMarketRegistry()
            .build(
                exchange_id="digifinex",
                comparison_result=comparison,
                native_markets=native_result.get(
                    "markets",
                    [],
                ),
            )
        )

        self._verified_raw_only = {
            item["symbol"]
            for item in registry.get(
                "verified_markets",
                [],
            )
            if item.get("verified") is True
            and item.get("source") == "RAW_ONLY"
        }
