"""
ArbOS™
EX-187
Native Coverage Prioritizer

Ranks exchange native-fallback implementation opportunities
using measured coverage and measured depth evidence only.

The prioritizer never extrapolates sampled depth results to
the full verified RAW_ONLY market population.

Research/public market-data infrastructure only.
No authentication.
No transfers.
No live orders.
"""


class NativeCoveragePrioritizer:
    def prioritize(
        self,
        audits,
    ):
        if audits is None:
            raise ValueError(
                "audits are required"
            )

        priorities = []
        excluded = []

        for audit in audits:
            if not isinstance(audit, dict):
                continue

            if audit.get(
                "scan_failed"
            ) is True:
                excluded.append(
                    audit
                )
                continue

            exchange_id = str(
                audit.get(
                    "exchange_id",
                    "",
                )
            ).strip().lower()

            verified_count = int(
                audit.get(
                    "verified_raw_only_count",
                    0,
                )
                or 0
            )

            sampled_count = int(
                audit.get(
                    "depth_sampled_count",
                    0,
                )
                or 0
            )

            usable_count = int(
                audit.get(
                    "usable_depth_count",
                    0,
                )
                or 0
            )

            usable_ratio = float(
                audit.get(
                    "usable_depth_ratio",
                    0.0,
                )
                or 0.0
            )

            fallback_coverage = str(
                audit.get(
                    "fallback_coverage",
                    "",
                )
            ).strip().upper()

            if (
                verified_count <= 0
                or fallback_coverage
                == "NOT_REQUIRED"
            ):
                implementation_status = (
                    "NOT_REQUIRED"
                )
                implementation_required = False
                priority_reason = (
                    "native_fallback_not_required"
                )

            elif fallback_coverage == "AVAILABLE":
                implementation_status = (
                    "IMPLEMENTED"
                )
                implementation_required = False

                if sampled_count > 0:
                    priority_reason = (
                        "implemented_native_coverage_"
                        "with_measured_depth"
                    )
                else:
                    priority_reason = (
                        "implemented_native_coverage_"
                        "without_depth_sample"
                    )

            else:
                implementation_status = (
                    "NEEDS_IMPLEMENTATION"
                )
                implementation_required = True

                if sampled_count > 0:
                    priority_reason = (
                        "unimplemented_native_coverage_"
                        "with_measured_depth"
                    )
                else:
                    priority_reason = (
                        "unimplemented_native_coverage_"
                        "without_depth_sample"
                    )

            priorities.append({
                "exchange_id": exchange_id,
                "verified_raw_only_count": (
                    verified_count
                ),
                "depth_sampled_count": (
                    sampled_count
                ),
                "usable_depth_count": (
                    usable_count
                ),
                "usable_depth_ratio": (
                    usable_ratio
                ),
                "fallback_coverage": (
                    fallback_coverage
                ),
                "implementation_status": (
                    implementation_status
                ),
                "implementation_required": (
                    implementation_required
                ),
                "priority_reason": (
                    priority_reason
                ),
            })

        status_rank = {
            "NEEDS_IMPLEMENTATION": 3,
            "IMPLEMENTED": 2,
            "NOT_REQUIRED": 1,
        }

        priorities = sorted(
            priorities,
            key=lambda item: (
                status_rank.get(
                    item[
                        "implementation_status"
                    ],
                    0,
                ),
                item[
                    "verified_raw_only_count"
                ],
                item[
                    "usable_depth_ratio"
                ],
                item[
                    "usable_depth_count"
                ],
                item[
                    "depth_sampled_count"
                ],
                item[
                    "exchange_id"
                ],
            ),
            reverse=True,
        )

        return {
            "priority_count": len(
                priorities
            ),
            "excluded_exchange_count": len(
                excluded
            ),
            "priorities": priorities,
            "excluded_exchanges": excluded,
            "priority_complete": True,
            "live_order_submitted": False,
        }
