"""
ArbOS™
EX-149
Profitable Opportunity Selector
"""

from exchanges.arbitrage_profit_evaluation import (
    ArbitrageProfitEvaluation,
)


class ProfitableOpportunitySelector:
    def select(
        self,
        routes,
        starting_value,
        minimum_profit_percent,
    ):
        if minimum_profit_percent < 0:
            raise ValueError(
                "minimum_profit_percent must be non-negative"
            )

        profitable_routes = []

        for route in routes:
            if route.get("executable") is not True:
                continue

            final_value = route.get(
                "net_final_value"
            )

            if final_value is None:
                continue

            evaluation = ArbitrageProfitEvaluation.evaluate(
                starting_value=starting_value,
                final_value=float(final_value),
                minimum_profit_percent=minimum_profit_percent,
            )

            if not evaluation.valid:
                continue

            if not evaluation.profitable:
                continue

            record = dict(route)
            record["profitability"] = {
                "profitable": evaluation.profitable,
                "net_profit": evaluation.net_profit,
                "profit_percent": evaluation.profit_percent,
                "reason": evaluation.reason,
            }

            profitable_routes.append(record)

        profitable_routes.sort(
            key=lambda route: (
                route["profitability"][
                    "profit_percent"
                ],
                route["profitability"][
                    "net_profit"
                ],
            ),
            reverse=True,
        )

        profitable_internal = [
            route
            for route in profitable_routes
            if route.get("route_type")
            == "internal_triangle"
        ]

        profitable_cross_exchange = [
            route
            for route in profitable_routes
            if route.get("route_type") in {
                "direct_cross_exchange",
                "bridge_cross_exchange",
            }
        ]

        return {
            "best_profitable_route": (
                profitable_routes[0]
                if profitable_routes
                else None
            ),
            "best_profitable_internal": (
                profitable_internal[0]
                if profitable_internal
                else None
            ),
            "best_profitable_cross_exchange": (
                profitable_cross_exchange[0]
                if profitable_cross_exchange
                else None
            ),
            "profitable_routes": profitable_routes,
            "profitable_route_count": len(
                profitable_routes
            ),
        }
