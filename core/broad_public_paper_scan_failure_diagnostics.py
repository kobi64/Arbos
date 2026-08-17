"""
ArbOS™
EX-257
Broad Public Paper Scan Failure Diagnostics

Builds operator-facing diagnostics from broad public paper
scan discovery failures, scanner failures, and rejected routes.

Observability/reporting only.
No authentication.
No transfers.
No live orders.
"""


class BroadPublicPaperScanFailureDiagnostics:
    def build(self, scan_result):
        if scan_result is None:
            raise ValueError(
                "scan_result is required"
            )

        discovery_failures = list(
            scan_result.get(
                "discovery_failures",
                [],
            )
            or []
        )

        scanner_failures = list(
            scan_result.get(
                "scanner_failures",
                [],
            )
            or []
        )

        rejected_routes = list(
            scan_result.get(
                "rejected_routes",
                [],
            )
            or []
        )

        failures = (
            discovery_failures
            + scanner_failures
        )

        failures_by_phase = {}
        failures_by_reason = {}
        failures_by_exchange = {}

        affected_coins = set()
        affected_exchange_pairs = set()

        for failure in failures:
            phase = (
                failure.get("phase")
                or (
                    "discovery"
                    if failure.get(
                        "reason"
                    )
                    == "universe_discovery_failed"
                    else "unknown"
                )
            )

            reason = (
                failure.get("reason")
                or "unknown"
            )

            failures_by_phase[phase] = (
                failures_by_phase.get(
                    phase,
                    0,
                )
                + 1
            )

            failures_by_reason[reason] = (
                failures_by_reason.get(
                    reason,
                    0,
                )
                + 1
            )

            exchange_id = failure.get(
                "exchange_id"
            )

            source_exchange_id = (
                failure.get(
                    "source_exchange_id"
                )
            )

            destination_exchange_id = (
                failure.get(
                    "destination_exchange_id"
                )
            )

            for item in (
                exchange_id,
                source_exchange_id,
                destination_exchange_id,
            ):
                if item:
                    failures_by_exchange[
                        item
                    ] = (
                        failures_by_exchange.get(
                            item,
                            0,
                        )
                        + 1
                    )

            coin_asset = failure.get(
                "coin_asset"
            )

            if coin_asset:
                affected_coins.add(
                    str(
                        coin_asset
                    ).strip().upper()
                )

            if (
                source_exchange_id
                and destination_exchange_id
            ):
                affected_exchange_pairs.add(
                    (
                        source_exchange_id,
                        destination_exchange_id,
                    )
                )

        rejection_reasons = {}
        feasibility_failures_by_reason = {}
        feasibility_failed_network_count = 0
        feasibility_rejected_route_count = 0

        for route in rejected_routes:
            reason = (
                route.get("reason")
                or "unknown"
            )

            rejection_reasons[reason] = (
                rejection_reasons.get(
                    reason,
                    0,
                )
                + 1
            )

            diagnostics = route.get(
                "feasibility_diagnostics"
            )

            if not isinstance(
                diagnostics,
                dict,
            ):
                continue

            feasibility_rejected_route_count += 1

            feasibility_failed_network_count += int(
                diagnostics.get(
                    "failed_network_count",
                    0,
                )
                or 0
            )

            failures_by_reason = diagnostics.get(
                "failures_by_reason",
                {},
            )

            if not isinstance(
                failures_by_reason,
                dict,
            ):
                continue

            for (
                failure_reason,
                count,
            ) in failures_by_reason.items():
                failure_reason = (
                    str(
                        failure_reason
                        or "unknown"
                    )
                )

                feasibility_failures_by_reason[
                    failure_reason
                ] = (
                    feasibility_failures_by_reason.get(
                        failure_reason,
                        0,
                    )
                    + int(count or 0)
                )

        total_failure_count = len(
            failures
        )

        rejected_route_count = len(
            rejected_routes
        )

        configured_exchange_count = int(
            scan_result.get(
                "configured_exchange_count",
                scan_result.get(
                    "exchange_count",
                    0,
                ),
            )
            or 0
        )

        discovered_exchange_count = int(
            scan_result.get(
                "discovered_exchange_count",
                configured_exchange_count,
            )
            or 0
        )

        if (
            configured_exchange_count > 0
            and discovered_exchange_count == 0
        ):
            status = "failed"
        elif (
            total_failure_count > 0
            or rejected_route_count > 0
        ):
            status = "degraded"
        else:
            status = "healthy"

        return {
            "status": status,
            "total_failure_count": (
                total_failure_count
            ),
            "discovery_failure_count": len(
                discovery_failures
            ),
            "scanner_failure_count": len(
                scanner_failures
            ),
            "rejected_route_count": (
                rejected_route_count
            ),
            "failures_by_phase": dict(
                sorted(
                    failures_by_phase.items()
                )
            ),
            "failures_by_reason": dict(
                sorted(
                    failures_by_reason.items()
                )
            ),
            "failures_by_exchange": dict(
                sorted(
                    failures_by_exchange.items()
                )
            ),
            "rejection_reasons": dict(
                sorted(
                    rejection_reasons.items()
                )
            ),
            "feasibility_rejected_route_count": (
                feasibility_rejected_route_count
            ),
            "feasibility_failed_network_count": (
                feasibility_failed_network_count
            ),
            "feasibility_failures_by_reason": dict(
                sorted(
                    feasibility_failures_by_reason.items()
                )
            ),
            "affected_coin_assets": sorted(
                affected_coins
            ),
            "affected_exchange_pairs": [
                {
                    "source_exchange": source,
                    "destination_exchange": (
                        destination
                    ),
                }
                for source, destination in sorted(
                    affected_exchange_pairs
                )
            ],
            "failures": [
                dict(failure)
                for failure in failures
            ],
            "paper_only": True,
            "live_order_submitted": False,
        }
