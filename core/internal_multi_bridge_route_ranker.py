"""
ArbOS™
EX-133
Internal Multi-Bridge Route Ranker
"""

from exchanges.opportunity_ranking import (
    OpportunityRanking,
)


class InternalMultiBridgeRouteRanker:
    def rank(self, results):
        if not results:
            return []

        ranking_inputs = []
        originals = {}

        for index, result in enumerate(results):
            if result.get("filled") is not True:
                continue

            key = f"route-{index}"

            ranking_inputs.append({
                "id": key,
                "executable": True,
                "profit_percent": result.get(
                    "net_profit_percent",
                    0.0,
                ),
                "net_profit": result.get(
                    "net_profit",
                    0.0,
                ),
            })

            originals[key] = result

        ranked = OpportunityRanking.rank(
            ranking_inputs
        )

        return [
            originals[item["id"]]
            for item in ranked
        ]
