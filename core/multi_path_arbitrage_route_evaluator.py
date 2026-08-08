"""
ArbOS™
EX-135
Multi-Path Arbitrage Route Evaluator
"""

from exchanges.opportunity_ranking import (
    OpportunityRanking,
)


class MultiPathArbitrageRouteEvaluator:
    def evaluate(self, candidates):
        if not candidates:
            return {
                "best_route": None,
                "ranked_routes": [],
                "executable_count": 0,
            }

        executable = [
            candidate
            for candidate in candidates
            if candidate.get("executable") is True
        ]

        ranking_inputs = []
        originals = {}

        for index, candidate in enumerate(executable):
            key = f"candidate-{index}"

            ranking_inputs.append({
                "id": key,
                "executable": True,
                "profit_percent": candidate.get(
                    "net_profit_percent",
                    0.0,
                ),
                "net_profit": candidate.get(
                    "net_profit",
                    0.0,
                ),
            })

            originals[key] = candidate

        ranked_inputs = OpportunityRanking.rank(
            ranking_inputs
        )

        ranked_routes = [
            originals[item["id"]]
            for item in ranked_inputs
        ]

        best_route = (
            ranked_routes[0]
            if ranked_routes
            else None
        )

        ranked_internal = [
            route
            for route in ranked_routes
            if route.get("route_type")
            == "internal_triangle"
        ]

        ranked_cross_exchange = [
            route
            for route in ranked_routes
            if route.get("route_type") in {
                "direct_cross_exchange",
                "bridge_cross_exchange",
            }
        ]

        best_internal = (
            ranked_internal[0]
            if ranked_internal
            else None
        )

        best_cross_exchange = (
            ranked_cross_exchange[0]
            if ranked_cross_exchange
            else None
        )

        return {
            "best_route": best_route,
            "ranked_routes": ranked_routes,
            "executable_count": len(ranked_routes),
            "best_internal": best_internal,
            "best_cross_exchange": best_cross_exchange,
            "ranked_internal": ranked_internal,
            "ranked_cross_exchange": (
                ranked_cross_exchange
            ),
        }
