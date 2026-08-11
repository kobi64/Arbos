"""
ArbOS™
EX-185
Native Fallback Coverage Auditor

Summarizes native market-discovery discrepancies and determines
whether verified RAW_ONLY markets are covered by a registered
native fallback provider.

Research and public market-data infrastructure only.
No authentication.
No transfers.
No live orders.
"""


class NativeFallbackCoverageAuditor:
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
        comparison_result,
        verified_registry,
    ):
        if (
            exchange_id is None
            or not str(exchange_id).strip()
        ):
            raise ValueError(
                "exchange_id is required"
            )

        if comparison_result is None:
            raise ValueError(
                "comparison_result is required"
            )

        if verified_registry is None:
            raise ValueError(
                "verified_registry is required"
            )

        exchange_id = str(
            exchange_id
        ).strip().lower()

        verified_raw_only = []

        for market in verified_registry.get(
            "verified_markets",
            [],
        ):
            if not isinstance(market, dict):
                continue

            if (
                market.get("verified") is not True
                or str(
                    market.get("source", "")
                ).strip().upper()
                != "RAW_ONLY"
            ):
                continue

            symbol = str(
                market.get("symbol", "")
            ).strip().upper()

            if symbol:
                verified_raw_only.append(
                    symbol
                )

        verified_raw_only = sorted(
            set(verified_raw_only)
        )

        rejected_raw_only = []

        for market in verified_registry.get(
            "rejected_markets",
            [],
        ):
            if not isinstance(market, dict):
                continue

            if (
                str(
                    market.get("source", "")
                ).strip().upper()
                != "RAW_ONLY"
            ):
                continue

            symbol = str(
                market.get("symbol", "")
            ).strip().upper()

            if not symbol:
                continue

            rejected_raw_only.append({
                "symbol": symbol,
                "reason": market.get(
                    "reason"
                ),
                "native_status": market.get(
                    "native_status"
                ),
                "order_types": market.get(
                    "order_types"
                ),
            })

        rejected_raw_only = sorted(
            rejected_raw_only,
            key=lambda item: item["symbol"],
        )

        fallback_registered = (
            self._fallback_registry.has(
                exchange_id
            )
        )

        if not verified_raw_only:
            fallback_coverage = (
                "NOT_REQUIRED"
            )
        elif fallback_registered:
            fallback_coverage = (
                "AVAILABLE"
            )
        else:
            fallback_coverage = (
                "NOT_IMPLEMENTED"
            )

        return {
            "exchange_id": exchange_id,
            "ccxt_market_count": (
                comparison_result.get(
                    "ccxt_market_count",
                    0,
                )
            ),
            "native_market_count": (
                comparison_result.get(
                    "raw_market_count",
                    0,
                )
            ),
            "matched_count": (
                comparison_result.get(
                    "matched_count",
                    0,
                )
            ),
            "ccxt_only_count": (
                comparison_result.get(
                    "ccxt_only_count",
                    0,
                )
            ),
            "ccxt_only": list(
                comparison_result.get(
                    "ccxt_only",
                    [],
                )
                or []
            ),
            "raw_only_count": (
                comparison_result.get(
                    "raw_only_count",
                    0,
                )
            ),
            "raw_only": list(
                comparison_result.get(
                    "raw_only",
                    [],
                )
                or []
            ),
            "verified_raw_only_count": len(
                verified_raw_only
            ),
            "verified_raw_only": (
                verified_raw_only
            ),
            "rejected_raw_only_count": len(
                rejected_raw_only
            ),
            "rejected_raw_only": (
                rejected_raw_only
            ),
            "fallback_registered": (
                fallback_registered
            ),
            "fallback_coverage": (
                fallback_coverage
            ),
            "audit_complete": True,
            "live_order_submitted": False,
        }
