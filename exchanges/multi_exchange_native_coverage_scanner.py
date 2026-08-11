"""
ArbOS™
EX-186
Multi-Exchange Native Coverage Scanner

Runs the EX-185 native fallback discovery audit across multiple
exchanges and ranks them by verified RAW_ONLY market coverage.

Research/public market-data infrastructure only.
No authentication.
No transfers.
No live orders.
"""

from exchanges.native_fallback_discovery_runner import (
    NativeFallbackDiscoveryRunner,
)
from exchanges.native_depth_usability_sampler import (
    NativeDepthUsabilitySampler,
)


class MultiExchangeNativeCoverageScanner:
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

    def scan(
        self,
        entries,
    ):
        if entries is None:
            raise ValueError(
                "entries are required"
            )

        audits = []

        runner = NativeFallbackDiscoveryRunner(
            fallback_registry=(
                self._fallback_registry
            )
        )

        for entry in entries:
            if not isinstance(entry, dict):
                continue

            exchange = entry.get(
                "exchange"
            )

            native_market_source = entry.get(
                "native_market_source"
            )

            if (
                exchange is None
                or native_market_source is None
            ):
                continue

            try:
                audit = runner.run(
                    exchange=exchange,
                    native_market_source=(
                        native_market_source
                    ),
                )
            except Exception as exc:
                exchange_id = str(
                    getattr(exchange, "id", "") or ""
                ).strip().lower()

                audits.append({
                    "exchange_id": exchange_id,
                    "scan_failed": True,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "audit_complete": False,
                    "fallback_coverage": "UNKNOWN",
                    "verified_raw_only_count": 0,
                    "raw_only_count": 0,
                    "live_order_submitted": False,
                })

                continue

            provider = entry.get(
                "order_book_provider"
            )

            sample_size = entry.get(
                "depth_sample_size",
                10,
            )

            verified_symbols = audit.get(
                "verified_raw_only",
                [],
            )

            if (
                provider is not None
                and verified_symbols
            ):
                depth_result = (
                    NativeDepthUsabilitySampler()
                    .sample(
                        symbols=verified_symbols,
                        provider=provider,
                        sample_size=sample_size,
                    )
                )
            else:
                depth_result = {
                    "sampled_count": 0,
                    "usable_depth_count": 0,
                    "failed_depth_count": 0,
                    "usable_depth_ratio": 0.0,
                    "usable_symbols": [],
                    "failed_symbols": [],
                    "sampling_complete": True,
                    "live_order_submitted": False,
                }

            audit = {
                **audit,
                "depth_sampled_count": (
                    depth_result[
                        "sampled_count"
                    ]
                ),
                "usable_depth_count": (
                    depth_result[
                        "usable_depth_count"
                    ]
                ),
                "failed_depth_count": (
                    depth_result[
                        "failed_depth_count"
                    ]
                ),
                "usable_depth_ratio": (
                    depth_result[
                        "usable_depth_ratio"
                    ]
                ),
                "usable_depth_symbols": (
                    depth_result[
                        "usable_symbols"
                    ]
                ),
                "failed_depth_symbols": (
                    depth_result[
                        "failed_symbols"
                    ]
                ),
            }

            audits.append(
                audit
            )

        successful_exchanges = [
            audit
            for audit in audits
            if audit.get("scan_failed") is not True
        ]

        failed_exchanges = [
            audit
            for audit in audits
            if audit.get("scan_failed") is True
        ]

        ranked_exchanges = sorted(
            successful_exchanges,
            key=lambda audit: (
                int(
                    audit.get(
                        "verified_raw_only_count",
                        0,
                    )
                    or 0
                ),
                int(
                    audit.get(
                        "raw_only_count",
                        0,
                    )
                    or 0
                ),
                str(
                    audit.get(
                        "exchange_id",
                        "",
                    )
                ),
            ),
            reverse=True,
        )

        return {
            "exchange_count": len(
                audits
            ),
            "successful_exchange_count": len(
                successful_exchanges
            ),
            "failed_exchange_count": len(
                failed_exchanges
            ),
            "failed_exchanges": failed_exchanges,
            "audits": audits,
            "ranked_exchanges": (
                ranked_exchanges
            ),
            "scan_complete": True,
            "live_order_submitted": False,
        }
