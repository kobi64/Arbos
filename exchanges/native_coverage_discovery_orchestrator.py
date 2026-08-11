"""
ArbOS™
EX-189
Native Coverage Discovery Orchestrator

Coordinates multi-exchange native coverage scanning and
implementation prioritization.

Composition only.
No authentication.
No transfers.
No live orders.
"""

from exchanges.multi_exchange_native_coverage_scanner import (
    MultiExchangeNativeCoverageScanner,
)
from exchanges.native_coverage_prioritizer import (
    NativeCoveragePrioritizer,
)


class NativeCoverageDiscoveryOrchestrator:
    def __init__(
        self,
        fallback_registry,
        scanner=None,
        prioritizer=None,
    ):
        if fallback_registry is None:
            raise ValueError(
                "fallback_registry is required"
            )

        self._fallback_registry = fallback_registry

        self._scanner = (
            scanner
            if scanner is not None
            else MultiExchangeNativeCoverageScanner(
                fallback_registry=fallback_registry
            )
        )

        self._prioritizer = (
            prioritizer
            if prioritizer is not None
            else NativeCoveragePrioritizer()
        )

    def run(
        self,
        entries,
    ):
        if entries is None:
            raise ValueError(
                "entries are required"
            )

        scan_result = self._scanner.scan(
            entries
        )

        audits = scan_result.get(
            "audits",
            [],
        )

        priority_result = (
            self._prioritizer.prioritize(
                audits
            )
        )

        return {
            "exchange_count": scan_result.get(
                "exchange_count",
                0,
            ),
            "successful_exchange_count": (
                scan_result.get(
                    "successful_exchange_count",
                    0,
                )
            ),
            "failed_exchange_count": (
                scan_result.get(
                    "failed_exchange_count",
                    0,
                )
            ),
            "failed_exchanges": (
                scan_result.get(
                    "failed_exchanges",
                    [],
                )
            ),
            "audits": audits,
            "ranked_exchanges": (
                scan_result.get(
                    "ranked_exchanges",
                    [],
                )
            ),
            "priority_count": (
                priority_result.get(
                    "priority_count",
                    0,
                )
            ),
            "excluded_exchange_count": (
                priority_result.get(
                    "excluded_exchange_count",
                    0,
                )
            ),
            "priorities": (
                priority_result.get(
                    "priorities",
                    [],
                )
            ),
            "excluded_exchanges": (
                priority_result.get(
                    "excluded_exchanges",
                    [],
                )
            ),
            "scan_complete": scan_result.get(
                "scan_complete",
                False,
            ),
            "priority_complete": (
                priority_result.get(
                    "priority_complete",
                    False,
                )
            ),
            "orchestration_complete": True,
            "live_order_submitted": False,
        }
