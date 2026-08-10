"""
ArbOS™
EX-182
Verified RAW_ONLY Market Source

Exchange-agnostic verifier for markets that exist in an
exchange-native catalogue but are missing from CCXT's normalized
market catalogue.

A RAW_ONLY market is considered verified only when EX-176 confirms
that its native metadata is actively tradable.

Public market verification only.
No authentication.
No transfers.
No live orders.
"""

from exchanges.exchange_market_completeness_validator import (
    ExchangeMarketCompletenessValidator,
)
from exchanges.verified_exchange_market_registry import (
    VerifiedExchangeMarketRegistry,
)


class VerifiedRawOnlyMarketSource:
    def __init__(
        self,
        exchange_id,
        exchange,
        native_market_source,
    ):
        if exchange_id is None or not str(exchange_id).strip():
            raise ValueError("exchange_id is required")

        if exchange is None:
            raise ValueError("exchange is required")

        if native_market_source is None:
            raise ValueError(
                "native_market_source is required"
            )

        self._exchange_id = str(
            exchange_id
        ).strip().lower()

        self._exchange = exchange
        self._native_market_source = (
            native_market_source
        )

        self._verified_raw_only = None

    def is_verified(self, symbol):
        if symbol is None or not str(symbol).strip():
            return False

        symbol = str(
            symbol
        ).strip().upper()

        if self._verified_raw_only is None:
            self._build()

        return symbol in self._verified_raw_only

    def _build(self):
        markets = self._exchange.load_markets()

        ccxt_symbols = list(
            (markets or {}).keys()
        )

        native_result = (
            self._native_market_source.fetch()
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
                exchange_id=self._exchange_id,
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
                exchange_id=self._exchange_id,
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
