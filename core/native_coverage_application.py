"""
ArbOS™
EX-191
Native Coverage Application

Top-level public native coverage application.

Builds the configured public CCXT exchange set and runs the
configuration-driven native coverage orchestration workflow.

Research/public market-data only.
No authentication.
No transfers.
No live orders.
"""

from core.native_coverage_exchange_set_registry import (
    NativeCoverageExchangeSetRegistry,
)
from exchanges.config_driven_native_coverage_orchestrator import (
    ConfigDrivenNativeCoverageOrchestrator,
)


class NativeCoverageApplication:
    def __init__(
        self,
        ccxt_module,
        fallback_registry,
        exchange_ids=None,
        coverage_orchestrator=None,
    ):
        if ccxt_module is None:
            raise ValueError(
                "ccxt_module is required"
            )

        if fallback_registry is None:
            raise ValueError(
                "fallback_registry is required"
            )

        self._exchange_set = (
            NativeCoverageExchangeSetRegistry(
                ccxt_module=ccxt_module,
                exchange_ids=exchange_ids,
            )
        )

        self._coverage_orchestrator = (
            coverage_orchestrator
            if coverage_orchestrator is not None
            else ConfigDrivenNativeCoverageOrchestrator(
                fallback_registry=(
                    fallback_registry
                )
            )
        )

    def set_enabled(
        self,
        exchange_id,
        enabled,
    ):
        self._exchange_set.set_enabled(
            exchange_id,
            enabled,
        )

    def enabled_exchange_ids(self):
        return (
            self._exchange_set
            .enabled_exchange_ids()
        )

    def run(self):
        exchanges = (
            self._exchange_set
            .build_exchange_map()
        )

        result = (
            self._coverage_orchestrator
            .run(exchanges)
        )

        return {
            **result,
            "configured_exchange_count": len(
                exchanges
            ),
            "enabled_exchange_ids": sorted(
                exchanges.keys()
            ),
            "live_order_submitted": False,
        }
