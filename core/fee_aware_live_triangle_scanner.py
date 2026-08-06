"""
ArbOS™
EX-116
Fee-Aware Live Triangle Scanner
"""

from exchanges.fee_aware_live_route_valuation import (
    FeeAwareLiveRouteValuation,
)


class FeeAwareLiveTriangleScanner:
    def __init__(self, market_data_provider):
        self._valuation = FeeAwareLiveRouteValuation(
            market_data_provider
        )

    def scan(self, routes, starting_value, fee_rate):
        if starting_value <= 0:
            raise ValueError("starting_value must be positive")

        if fee_rate < 0:
            raise ValueError("fee_rate must be non-negative")

        results = []

        for route in routes:
            fee_route = {
                "route_id": route.get("route_id"),
                "legs": [],
            }

            for leg in route.get("legs") or []:
                priced_leg = dict(leg)
                priced_leg["fee_rate"] = float(fee_rate)
                fee_route["legs"].append(priced_leg)

            valuation = self._valuation.evaluate(
                route=fee_route,
                starting_value=starting_value,
            )

            net_final_value = valuation["gross_final_value"]
            net_profit = net_final_value - float(starting_value)
            net_profit_percent = (
                net_profit / float(starting_value)
            ) * 100.0

            results.append({
                "route_id": valuation["route_id"],
                "starting_value": float(starting_value),
                "net_final_value": net_final_value,
                "net_profit": net_profit,
                "net_profit_percent": net_profit_percent,
                "total_fee_rate_effect": valuation["total_fee_rate_effect"],
                "legs": valuation["legs"],
                "paper_only": True,
                "live_order_submitted": False,
            })

        results.sort(
            key=lambda result: result["net_profit_percent"],
            reverse=True,
        )

        return results
