"""
ArbOS™
EX-185
Native Fallback Discovery Runner

Discovers an exchange's normalized CCXT market catalogue,
retrieves its native public market catalogue, and produces
a verified native-fallback coverage audit.

Research/public market-data infrastructure only.
No authentication.
No transfers.
No live orders.
"""

from exchanges.native_fallback_coverage_coordinator import (
    NativeFallbackCoverageCoordinator,
)
from exchanges.exchange_market_alias_reconciler import (
    ExchangeMarketAliasReconciler,
)


class NativeFallbackDiscoveryRunner:
    def __init__(
        self,
        fallback_registry,
    ):
        if fallback_registry is None:
            raise ValueError(
                "fallback_registry is required"
            )

        self._fallback_registry = (
            fallback_registry
        )

    def run(
        self,
        exchange,
        native_market_source,
    ):
        if exchange is None:
            raise ValueError(
                "exchange is required"
            )

        if native_market_source is None:
            raise ValueError(
                "native_market_source is required"
            )

        exchange_id = str(
            getattr(
                exchange,
                "id",
                "",
            )
            or ""
        ).strip().lower()

        if not exchange_id:
            raise ValueError(
                "exchange id is required"
            )

        markets = exchange.load_markets()

        ccxt_spot_markets = {
            str(symbol).strip().upper(): market
            for symbol, market in (
                (markets or {}).items()
            )
            if str(symbol).strip()
            and isinstance(market, dict)
            and market.get("spot") is True
        }

        ccxt_symbols = sorted(
            ccxt_spot_markets.keys()
        )

        ccxt_active_spot_count = sum(
            1
            for market in ccxt_spot_markets.values()
            if market.get(
                "active",
                True,
            ) is not False
        )

        ccxt_inactive_spot_count = (
            len(ccxt_spot_markets)
            - ccxt_active_spot_count
        )

        native_result = (
            native_market_source.fetch()
        )

        alias_result = (
            ExchangeMarketAliasReconciler()
            .reconcile(
                ccxt_markets=markets or {},
                native_markets=native_result.get(
                    "markets",
                    [],
                ),
            )
        )

        alias_matches = alias_result.get(
            "alias_matches",
            [],
        )

        alias_ccxt_symbols = {
            item["ccxt_symbol"]
            for item in alias_matches
        }

        alias_native_symbols = {
            item["native_symbol"]
            for item in alias_matches
        }

        reconciled_ccxt_symbols = [
            symbol
            for symbol in ccxt_symbols
            if symbol not in alias_ccxt_symbols
        ]

        native_symbols = [
            str(symbol).strip().upper()
            for symbol in native_result.get(
                "symbols",
                [],
            )
            if str(symbol).strip()
        ]

        reconciled_native_symbols = [
            symbol
            for symbol in native_symbols
            if symbol not in alias_native_symbols
        ]

        reconciled_native_result = {
            **native_result,
            "symbols": reconciled_native_symbols,
        }

        audit = (
            NativeFallbackCoverageCoordinator(
                fallback_registry=(
                    self._fallback_registry
                )
            ).audit(
                exchange_id=exchange_id,
                ccxt_symbols=(
                    reconciled_ccxt_symbols
                ),
                native_result=(
                    reconciled_native_result
                ),
            )
        )

        return {
            **audit,
            "ccxt_symbols": ccxt_symbols,
            "discovered_ccxt_market_count": len(
                ccxt_symbols
            ),
            "discovered_ccxt_active_spot_count": (
                ccxt_active_spot_count
            ),
            "discovered_ccxt_inactive_spot_count": (
                ccxt_inactive_spot_count
            ),
            "discovered_native_market_count": len(
                native_symbols
            ),
            "reconciled_ccxt_market_count": (
                audit.get(
                    "ccxt_market_count",
                    0,
                )
            ),
            "reconciled_native_market_count": (
                audit.get(
                    "native_market_count",
                    0,
                )
            ),
            "alias_match_count": (
                alias_result.get(
                    "alias_match_count",
                    0,
                )
            ),
            "alias_matches": (
                alias_matches
            ),
            "native_source": type(
                native_market_source
            ).__name__,
            "live_order_submitted": False,
        }
