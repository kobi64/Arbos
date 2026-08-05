"""
ArbOS™
EX-104
Opportunity Priority Scoring Engine
"""


class OpportunityPriorityScoringEngine:
    def score(
        self,
        net_profit_percent,
        liquidity_score,
        reliability_score,
        age_seconds,
        route_complexity,
    ):
        if age_seconds < 0:
            raise ValueError("age_seconds cannot be negative")

        if route_complexity <= 0:
            raise ValueError("route_complexity must be positive")

        profit_component = min(
            max(float(net_profit_percent), 0.0) * 20.0,
            40.0,
        )
        liquidity_component = min(
            max(float(liquidity_score), 0.0),
            100.0,
        ) * 0.25
        reliability_component = min(
            max(float(reliability_score), 0.0),
            100.0,
        ) * 0.25

        age_penalty = min(float(age_seconds) * 0.10, 20.0)
        complexity_penalty = max(
            float(route_complexity) - 1.0,
            0.0,
        ) * 2.0

        raw_score = (
            profit_component
            + liquidity_component
            + reliability_component
            - age_penalty
            - complexity_penalty
        )

        score = round(min(max(raw_score, 0.0), 100.0), 6)

        return {
            "score": score,
            "priority": score,
        }
