"""
ArbOS™
EX-192
Native Coverage Health Report

Builds a stable machine-readable health snapshot from a completed
native coverage orchestration result.

Observability/reporting only.
No authentication.
No transfers.
No live orders.
"""


class NativeCoverageHealthReport:
    def build(
        self,
        coverage_result,
    ):
        if coverage_result is None:
            raise ValueError(
                "coverage_result is required"
            )

        audits = coverage_result.get(
            "audits",
            [],
        )

        verified_raw_only_count = 0
        depth_sampled_count = 0
        usable_depth_count = 0

        fallback_available_exchange_ids = []
        failed_exchange_ids = []

        for audit in audits:
            if not isinstance(audit, dict):
                continue

            exchange_id = str(
                audit.get(
                    "exchange_id",
                    "",
                )
                or ""
            ).strip().lower()

            verified_raw_only_count += int(
                audit.get(
                    "verified_raw_only_count",
                    0,
                )
                or 0
            )

            depth_sampled_count += int(
                audit.get(
                    "depth_sampled_count",
                    0,
                )
                or 0
            )

            usable_depth_count += int(
                audit.get(
                    "usable_depth_count",
                    0,
                )
                or 0
            )

            fallback_coverage = str(
                audit.get(
                    "fallback_coverage",
                    "",
                )
                or ""
            ).strip().upper()

            if (
                fallback_coverage == "AVAILABLE"
                and exchange_id
            ):
                fallback_available_exchange_ids.append(
                    exchange_id
                )

            if (
                audit.get("scan_failed")
                and exchange_id
            ):
                failed_exchange_ids.append(
                    exchange_id
                )

        fallback_available_exchange_ids = sorted(
            set(
                fallback_available_exchange_ids
            )
        )

        failed_exchange_ids = sorted(
            set(
                failed_exchange_ids
            )
        )

        failed_exchange_count = int(
            coverage_result.get(
                "failed_exchange_count",
                0,
            )
            or 0
        )

        orchestration_complete = bool(
            coverage_result.get(
                "orchestration_complete",
                False,
            )
        )

        healthy = (
            orchestration_complete
            and failed_exchange_count == 0
            and not failed_exchange_ids
        )

        return {
            "status": (
                "HEALTHY"
                if healthy
                else "DEGRADED"
            ),
            "healthy": healthy,
            "configured_exchange_count": int(
                coverage_result.get(
                    "configured_exchange_count",
                    0,
                )
                or 0
            ),
            "successful_exchange_count": int(
                coverage_result.get(
                    "successful_exchange_count",
                    0,
                )
                or 0
            ),
            "failed_exchange_count": (
                failed_exchange_count
            ),
            "enabled_exchange_ids": list(
                coverage_result.get(
                    "enabled_exchange_ids",
                    [],
                )
                or []
            ),
            "verified_raw_only_count": (
                verified_raw_only_count
            ),
            "depth_sampled_count": (
                depth_sampled_count
            ),
            "usable_depth_count": (
                usable_depth_count
            ),
            "fallback_available_exchange_ids": (
                fallback_available_exchange_ids
            ),
            "failed_exchange_ids": (
                failed_exchange_ids
            ),
            "priorities": list(
                coverage_result.get(
                    "priorities",
                    [],
                )
                or []
            ),
            "orchestration_complete": (
                orchestration_complete
            ),
            "report_complete": True,
            "live_order_submitted": False,
        }
