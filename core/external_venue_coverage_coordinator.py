"""
ArbOS™
EX-216
External Venue Coverage Coordinator

Evaluates external-intelligence opportunities against the
current ArbOS™ venue capability registry and records real
coverage demand for future exchange expansion.

Responsibilities:
- classify each route
- preserve original opportunity metadata
- record venue demand
- summarize coverage levels
- produce exchange integration priority

Paper-safe only.
No live orders.
"""


class ExternalVenueCoverageCoordinator:
    def __init__(
        self,
        registry,
        tracker,
    ):
        if registry is None:
            raise ValueError(
                "registry is required"
            )

        if tracker is None:
            raise ValueError(
                "tracker is required"
            )

        self._registry = registry
        self._tracker = tracker

    def evaluate(
        self,
        opportunities,
    ):
        routes = []

        full_count = 0
        partial_count = 0
        intelligence_only_count = 0
        unsupported_count = 0

        for opportunity in (
            opportunities
            or []
        ):
            buy_exchange = (
                opportunity.get(
                    "buy_exchange"
                )
            )

            sell_exchange = (
                opportunity.get(
                    "sell_exchange"
                )
            )

            coverage = (
                self._registry.classify_route(
                    buy_exchange=buy_exchange,
                    sell_exchange=sell_exchange,
                )
            )

            record = {
                **dict(opportunity),
                "coverage": coverage[
                    "coverage"
                ],
                "full_verification_available": (
                    coverage[
                        "full_verification_available"
                    ]
                ),
                "unsupported_exchanges": list(
                    coverage.get(
                        "unsupported_exchanges"
                    )
                    or []
                ),
                "buy_capability": coverage.get(
                    "buy_capability"
                ),
                "sell_capability": coverage.get(
                    "sell_capability"
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

            routes.append(
                record
            )

            self._tracker.record_route(
                opportunity=opportunity,
                coverage=coverage,
            )

            level = coverage[
                "coverage"
            ]

            if level == "full":
                full_count += 1
            elif level == "partial":
                partial_count += 1
            elif level == "intelligence_only":
                intelligence_only_count += 1
            elif level == "unsupported":
                unsupported_count += 1

        return {
            "route_count": len(
                routes
            ),
            "full_count": (
                full_count
            ),
            "partial_count": (
                partial_count
            ),
            "intelligence_only_count": (
                intelligence_only_count
            ),
            "unsupported_count": (
                unsupported_count
            ),
            "routes": routes,
            "integration_priority": (
                self._tracker.priority_ranking()
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
