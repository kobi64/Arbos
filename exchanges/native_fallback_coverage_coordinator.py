"""
ArbOS™
EX-185
Native Fallback Coverage Coordinator

Combines:
- EX-176 market completeness validation
- EX-176 verified exchange market registry
- EX-185 native fallback coverage audit

Research/public market-data infrastructure only.
No authentication.
No transfers.
No live orders.
"""

from exchanges.exchange_market_completeness_validator import (
    ExchangeMarketCompletenessValidator,
)
from exchanges.native_fallback_coverage_auditor import (
    NativeFallbackCoverageAuditor,
)
from exchanges.verified_exchange_market_registry import (
    VerifiedExchangeMarketRegistry,
)


class NativeFallbackCoverageCoordinator:
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

    def audit(
        self,
        exchange_id,
        ccxt_symbols,
        native_result,
    ):
        if (
            exchange_id is None
            or not str(exchange_id).strip()
        ):
            raise ValueError(
                "exchange_id is required"
            )

        if ccxt_symbols is None:
            raise ValueError(
                "ccxt_symbols is required"
            )

        if native_result is None:
            raise ValueError(
                "native_result is required"
            )

        exchange_id = str(
            exchange_id
        ).strip().lower()

        if (
            native_result.get(
                "fetch_complete"
            )
            is not True
        ):
            return {
                "exchange_id": exchange_id,
                "native_fetch_complete": False,
                "audit_complete": False,
                "fallback_coverage": "UNKNOWN",
                "live_order_submitted": False,
            }

        comparison = (
            ExchangeMarketCompletenessValidator()
            .validate(
                exchange_id=exchange_id,
                ccxt_symbols=ccxt_symbols,
                raw_symbols=native_result.get(
                    "symbols",
                    [],
                ),
            )
        )

        verified_registry = (
            VerifiedExchangeMarketRegistry()
            .build(
                exchange_id=exchange_id,
                comparison_result=comparison,
                native_markets=native_result.get(
                    "markets",
                    [],
                ),
            )
        )

        audit = (
            NativeFallbackCoverageAuditor(
                fallback_registry=(
                    self._fallback_registry
                )
            ).audit(
                exchange_id=exchange_id,
                comparison_result=comparison,
                verified_registry=verified_registry,
            )
        )

        return {
            **audit,
            "native_fetch_complete": True,
            "audit_complete": True,
            "live_order_submitted": False,
        }
