"""
ArbOS™
EX-216
External Venue Coverage Demand Tracker

Tracks how often exchanges appear in external-intelligence
routes and how often those venues block or limit full
ArbOS™ verification.

Used to prioritize future exchange integrations based on
real observed demand from external sources.

Paper-safe only.
No live orders.
"""

from copy import deepcopy


class ExternalVenueCoverageDemandTracker:
    def __init__(self):
        self._exchange_stats = {}

    def record_route(
        self,
        opportunity,
        coverage,
    ):
        if opportunity is None:
            raise ValueError(
                "opportunity is required"
            )

        buy_exchange = str(
            opportunity.get(
                "buy_exchange",
                "",
            )
            or ""
        ).strip().lower()

        sell_exchange = str(
            opportunity.get(
                "sell_exchange",
                "",
            )
            or ""
        ).strip().lower()

        if not buy_exchange:
            raise ValueError(
                "buy_exchange is required"
            )

        if not sell_exchange:
            raise ValueError(
                "sell_exchange is required"
            )

        sources = [
            str(source).strip().lower()
            for source in (
                opportunity.get(
                    "sources"
                )
                or []
            )
            if str(
                source
            ).strip()
        ]

        route_coverage = str(
            coverage.get(
                "coverage",
                "",
            )
            or ""
        ).strip().lower()

        unsupported_exchanges = {
            str(exchange).strip().lower()
            for exchange in (
                coverage.get(
                    "unsupported_exchanges"
                )
                or []
            )
            if str(
                exchange
            ).strip()
        }

        for exchange in [
            buy_exchange,
            sell_exchange,
        ]:
            stats = self._require_stats(
                exchange
            )

            stats[
                "route_mentions"
            ] += 1

            if (
                exchange
                in unsupported_exchanges
            ):
                stats[
                    "unsupported_mentions"
                ] += 1

            elif route_coverage == "partial":
                stats[
                    "partial_mentions"
                ] += 1

            for source in sources:
                if (
                    source
                    not in stats[
                        "sources"
                    ]
                ):
                    stats[
                        "sources"
                    ].append(
                        source
                    )

        return {
            "recorded": True,
            "opportunity_key": (
                opportunity.get(
                    "opportunity_key"
                )
            ),
            "buy_exchange": (
                buy_exchange
            ),
            "sell_exchange": (
                sell_exchange
            ),
            "coverage": (
                route_coverage
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def exchange_statistics(
        self,
        exchange,
    ):
        exchange = str(
            exchange
            or ""
        ).strip().lower()

        if not exchange:
            raise ValueError(
                "exchange is required"
            )

        stats = self._exchange_stats.get(
            exchange
        )

        if stats is None:
            return {
                "exchange": exchange,
                "route_mentions": 0,
                "unsupported_mentions": 0,
                "partial_mentions": 0,
                "sources": [],
                "paper_only": True,
                "live_order_submitted": False,
            }

        return {
            **deepcopy(
                stats
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def priority_ranking(self):
        ranking = [
            deepcopy(
                stats
            )
            for stats in (
                self._exchange_stats.values()
            )
        ]

        ranking.sort(
            key=lambda item: (
                item[
                    "unsupported_mentions"
                ],
                item[
                    "partial_mentions"
                ],
                item[
                    "route_mentions"
                ],
                item[
                    "exchange"
                ],
            ),
            reverse=True,
        )

        for index, item in enumerate(
            ranking,
            start=1,
        ):
            item[
                "priority_rank"
            ] = index

            item[
                "paper_only"
            ] = True

            item[
                "live_order_submitted"
            ] = False

        return ranking

    def _require_stats(
        self,
        exchange,
    ):
        stats = self._exchange_stats.get(
            exchange
        )

        if stats is None:
            stats = {
                "exchange": exchange,
                "route_mentions": 0,
                "unsupported_mentions": 0,
                "partial_mentions": 0,
                "sources": [],
            }

            self._exchange_stats[
                exchange
            ] = stats

        return stats
