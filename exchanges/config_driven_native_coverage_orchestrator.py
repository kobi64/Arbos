"""
ArbOS™
EX-190
Configuration-Driven Native Coverage Orchestrator

Builds native coverage entries from configured exchange objects
and runs the EX-189 coverage orchestration pipeline.

Configuration/composition only.
No authentication.
No transfers.
No live orders.
"""

from exchanges.native_coverage_entry_factory import (
    NativeCoverageEntryFactory,
)
from exchanges.native_coverage_discovery_orchestrator import (
    NativeCoverageDiscoveryOrchestrator,
)
from exchanges.verified_digifinex_order_book_provider import (
    VerifiedDigiFinexOrderBookProvider,
)


class ConfigDrivenNativeCoverageOrchestrator:
    def __init__(
        self,
        fallback_registry,
        entry_factory=None,
        orchestrator=None,
    ):
        if fallback_registry is None:
            raise ValueError(
                "fallback_registry is required"
            )

        self._fallback_registry = (
            fallback_registry
        )

        self._entry_factory = (
            entry_factory
            if entry_factory is not None
            else NativeCoverageEntryFactory(
                provider_factories={
                    "digifinex": (
                        VerifiedDigiFinexOrderBookProvider
                    ),
                },
                depth_sample_sizes={
                    "digifinex": 20,
                },
            )
        )

        self._orchestrator = (
            orchestrator
            if orchestrator is not None
            else NativeCoverageDiscoveryOrchestrator(
                fallback_registry=(
                    fallback_registry
                )
            )
        )

    def run(
        self,
        exchanges,
    ):
        if exchanges is None:
            raise ValueError(
                "exchanges are required"
            )

        build_result = (
            self._entry_factory.build(
                exchanges
            )
        )

        entries = build_result.get(
            "entries",
            [],
        )

        orchestration_result = (
            self._orchestrator.run(
                entries
            )
        )

        return {
            **orchestration_result,
            "entry_count": build_result.get(
                "entry_count",
                0,
            ),
            "unsupported_exchange_count": (
                build_result.get(
                    "unsupported_exchange_count",
                    0,
                )
            ),
            "unsupported_exchange_ids": (
                build_result.get(
                    "unsupported_exchange_ids",
                    [],
                )
            ),
            "invalid_exchange_count": (
                build_result.get(
                    "invalid_exchange_count",
                    0,
                )
            ),
            "entry_build_complete": (
                build_result.get(
                    "build_complete",
                    False,
                )
            ),
            "live_order_submitted": False,
        }
