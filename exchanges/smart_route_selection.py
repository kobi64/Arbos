"""
ArbOS™
EX-037
Smart Route Selection Engine

Selects the best arbitrage route using:
- Expected profit
- Reliability score
- Execution duration

Purpose:
Rank routes by probability of successful realised profit.
"""

from datetime import datetime, UTC


class SmartRouteSelection:

    def __init__(self):
        self.routes = []

        self._history = [
            {
                "action": "selector_created",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ]

    def add_route(
        self,
        route_id: str,
        profit: float,
        reliability: float,
        duration: float,
    ):

        route = {
            "route_id": route_id,
            "profit": profit,
            "reliability": reliability,
            "duration": duration,
        }

        self.routes.append(route)

        return route

    def get_routes(self):

        return self.routes

    def _calculate_score(self, route):

        profit_score = min(route["profit"], 100)

        reliability_score = route["reliability"]

        duration_penalty = min(
            route["duration"] / 10,
            20,
        )

        score = (
            profit_score * 0.35
            + reliability_score * 0.65
            - duration_penalty
        )

        return round(score, 2)

    def select_best_route(self):

        if not self.routes:
            return None

        scored_routes = []

        for route in self.routes:

            scored_route = {
                **route,
                "score": self._calculate_score(route),
            }

            scored_routes.append(scored_route)

        best_route = max(
            scored_routes,
            key=lambda route: route["score"],
        )

        result = {
            **best_route,
            "reason": (
                "Selected based on combined "
                "profit, reliability and execution speed"
            ),
        }

        self._history.append(
            {
                "action": "route_selected",
                **result,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return result

    def get_history(self):

        return self._history
