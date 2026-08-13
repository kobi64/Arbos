"""
ArbOS™
EX-214
Multi-Source External Intelligence Orchestrator

Runs multiple external spot-intelligence coordinators and
combines their candidates into a unified opportunity view.

Responsibilities:
- run all registered external sources
- isolate individual source failures
- preserve source-level results
- combine candidates
- group identical opportunities
- detect multi-source consensus
- prioritize consensus opportunities

External intelligence remains advisory only.

No perpetuals.
No futures.
No live orders.
"""

from copy import deepcopy


class MultiSourceExternalIntelligenceOrchestrator:
    def __init__(
        self,
        coordinators,
    ):
        if not coordinators:
            raise ValueError(
                "coordinators are required"
            )

        self._coordinators = dict(
            coordinators
        )

        for source, coordinator in (
            self._coordinators.items()
        ):
            if coordinator is None:
                raise ValueError(
                    "coordinator is required "
                    f"for {source}"
                )

    def run_once(self):
        source_results = {}
        candidates = []
        failed_sources = []

        for source, coordinator in (
            self._coordinators.items()
        ):
            try:
                result = (
                    coordinator.run_once()
                )
            except Exception as exc:
                result = {
                    "fetch_complete": False,
                    "reason": (
                        "coordinator_exception"
                    ),
                    "error": str(exc),
                    "candidate_count": 0,
                    "candidates": [],
                    "paper_only": True,
                    "live_order_submitted": False,
                }

            source_results[source] = (
                deepcopy(result)
            )

            if (
                result.get(
                    "fetch_complete"
                )
                is not True
            ):
                failed_sources.append(
                    source
                )
                continue

            for candidate in (
                result.get(
                    "candidates"
                )
                or []
            ):
                candidates.append(
                    deepcopy(candidate)
                )

        grouped = {}

        for item in candidates:
            opportunity_key = (
                item.get(
                    "opportunity_key"
                )
            )

            if not opportunity_key:
                continue

            if (
                opportunity_key
                not in grouped
            ):
                grouped[
                    opportunity_key
                ] = {
                    "opportunity_key": (
                        opportunity_key
                    ),
                    "coin": item.get(
                        "coin"
                    ),
                    "buy_exchange": (
                        item.get(
                            "buy_exchange"
                        )
                    ),
                    "sell_exchange": (
                        item.get(
                            "sell_exchange"
                        )
                    ),
                    "sources": [],
                    "source_count": 0,
                    "signal_count": 0,
                    "signals": [],
                    "maximum_reported_spread_percent": None,
                    "verification_required": True,
                    "arbos_verified": False,
                    "executable": False,
                    "paper_only": True,
                    "live_order_submitted": False,
                }

            group = grouped[
                opportunity_key
            ]

            source = item.get(
                "source"
            )

            if (
                source
                and source
                not in group[
                    "sources"
                ]
            ):
                group[
                    "sources"
                ].append(
                    source
                )

            group[
                "signal_count"
            ] += 1

            group[
                "signals"
            ].append(
                deepcopy(item)
            )

            spread = item.get(
                "reported_spread_percent"
            )

            if spread is not None:
                spread = float(
                    spread
                )

                current = group[
                    "maximum_reported_spread_percent"
                ]

                if (
                    current is None
                    or spread > current
                ):
                    group[
                        "maximum_reported_spread_percent"
                    ] = spread

        opportunities = list(
            grouped.values()
        )

        for group in opportunities:
            group[
                "source_count"
            ] = len(
                group[
                    "sources"
                ]
            )

            group[
                "consensus"
            ] = (
                group[
                    "source_count"
                ]
                >= 2
            )

        # Consensus is deliberately the primary ranking
        # factor. A spectacular spread from one external
        # source must not outrank independently corroborated
        # intelligence merely because its claimed percentage
        # is larger.
        opportunities.sort(
            key=lambda item: (
                item[
                    "source_count"
                ],
                item[
                    "signal_count"
                ],
                (
                    item[
                        "maximum_reported_spread_percent"
                    ]
                    if item[
                        "maximum_reported_spread_percent"
                    ]
                    is not None
                    else float("-inf")
                ),
                item[
                    "opportunity_key"
                ],
            ),
            reverse=True,
        )

        verification_queue = []

        for index, opportunity in enumerate(
            opportunities,
            start=1,
        ):
            queue_item = deepcopy(
                opportunity
            )

            queue_item[
                "priority_rank"
            ] = index

            queue_item[
                "arbos_verified"
            ] = False

            queue_item[
                "executable"
            ] = False

            queue_item[
                "verification_required"
            ] = True

            queue_item[
                "paper_only"
            ] = True

            queue_item[
                "live_order_submitted"
            ] = False

            verification_queue.append(
                queue_item
            )

        return {
            "source_count": len(
                self._coordinators
            ),
            "successful_source_count": (
                len(
                    self._coordinators
                )
                - len(
                    failed_sources
                )
            ),
            "failed_source_count": len(
                failed_sources
            ),
            "failed_sources": (
                failed_sources
            ),
            "candidate_count": len(
                candidates
            ),
            "unique_opportunity_count": (
                len(
                    opportunities
                )
            ),
            "consensus_opportunity_count": sum(
                1
                for item in opportunities
                if item[
                    "consensus"
                ]
            ),
            "candidates": candidates,
            "opportunities": (
                opportunities
            ),
            "verification_queue": (
                verification_queue
            ),
            "verification_queue_count": len(
                verification_queue
            ),
            "source_results": (
                source_results
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def verify_queue(
        self,
        verification_queue,
        bridge,
        fee_rates,
        starting_usdt_value,
        max_slippage_percent=0.5,
        minimum_profit_percent=0.0,
        max_opportunities=None,
    ):
        if bridge is None:
            raise ValueError(
                "bridge is required"
            )

        starting_usdt_value = float(
            starting_usdt_value
        )

        if starting_usdt_value <= 0:
            raise ValueError(
                "starting_usdt_value must be positive"
            )

        if max_opportunities is not None:
            max_opportunities = int(
                max_opportunities
            )

            if max_opportunities <= 0:
                raise ValueError(
                    "max_opportunities must be positive"
                )

        full_queue = list(
            verification_queue
            or []
        )

        if max_opportunities is None:
            active_queue = full_queue
            deferred_opportunities = []
        else:
            active_queue = full_queue[
                :max_opportunities
            ]
            deferred_opportunities = full_queue[
                max_opportunities:
            ]

        results = []
        verification_failures = []
        attempted_count = 0

        for item in active_queue:
            buy_exchange = str(
                item.get(
                    "buy_exchange",
                    "",
                )
                or ""
            ).strip().lower()

            sell_exchange = str(
                item.get(
                    "sell_exchange",
                    "",
                )
                or ""
            ).strip().lower()

            if buy_exchange not in fee_rates:
                raise ValueError(
                    "fee rate is required for "
                    f"{buy_exchange}"
                )

            if sell_exchange not in fee_rates:
                raise ValueError(
                    "fee rate is required for "
                    f"{sell_exchange}"
                )

            attempted_count += 1

            try:
                verified = bridge.verify(
                    item,
                    starting_usdt_value=(
                        starting_usdt_value
                    ),
                    source_fee_rate=float(
                        fee_rates[
                            buy_exchange
                        ]
                    ),
                    destination_fee_rate=float(
                        fee_rates[
                            sell_exchange
                        ]
                    ),
                    max_slippage_percent=float(
                        max_slippage_percent
                    ),
                    minimum_profit_percent=float(
                        minimum_profit_percent
                    ),
                )

            except Exception as exc:
                failure = {
                    **dict(item),
                    "reason": (
                        "verification_exception"
                    ),
                    "error": (
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    ),
                    "arbos_verified": False,
                    "executable": False,
                    "verification_required": True,
                    "paper_only": True,
                    "live_order_submitted": False,
                }

                verification_failures.append(
                    failure
                )

                continue

            record = dict(
                verified
            )

            record[
                "priority_rank"
            ] = item.get(
                "priority_rank"
            )

            record[
                "paper_only"
            ] = True

            record[
                "live_order_submitted"
            ] = False

            results.append(
                record
            )

        return {
            "attempted_count": attempted_count,
            "verified_count": len(
                results
            ),
            "failed_verification_count": len(
                verification_failures
            ),
            "results": results,
            "verification_failures": (
                verification_failures
            ),
            "deferred_count": len(
                deferred_opportunities
            ),
            "deferred_opportunities": [
                dict(item)
                for item
                in deferred_opportunities
            ],
            "paper_only": True,
            "live_order_submitted": False,
        }
