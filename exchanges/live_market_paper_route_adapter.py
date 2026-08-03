"""
ArbOS™
EX-076
Live Market Paper Route Adapter
"""


class LiveMarketPaperRouteAdapter:
    def __init__(self, market_data_provider):
        self._provider = market_data_provider

    def adapt(self, route):
        if route is None:
            raise ValueError("route is required")

        route_id = route.get("route_id")
        legs = route.get("legs") or []

        adapted_legs = []

        result = {
            "route_id": route_id,
            "legs": adapted_legs,
            "live_market": True,
        }

        for leg in legs:
            symbol = leg.get("symbol")
            market_price = self._provider.get_price(symbol)

            if market_price is None:
                raise ValueError("market price unavailable")
            priced_leg = dict(leg)
            priced_leg["market_price"] = market_price
            adapted_legs.append(priced_leg)

        return result
