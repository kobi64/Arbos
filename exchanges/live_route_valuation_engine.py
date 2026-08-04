"""
ArbOS™
EX-087
Live Route Valuation Engine
"""


class LiveRouteValuationEngine:
    def __init__(self, market_data_provider):
        self._provider = market_data_provider

    def evaluate(self, route, starting_value):
        if route is None:
            raise ValueError("route is required")

        if starting_value <= 0:
            raise ValueError("starting_value must be positive")

        amount = float(starting_value)
        executed_legs = []

        for index, leg in enumerate(route.get("legs") or [], start=1):
            symbol = leg.get("symbol")
            side = str(leg.get("side", "")).strip().lower()

            if side == "buy":
                price = float(self._provider.get_ask(symbol))
                output_amount = amount / price
            elif side == "sell":
                price = float(self._provider.get_bid(symbol))
                output_amount = amount * price
            else:
                raise ValueError("invalid side")

            executed_legs.append({
                "leg_number": index,
                "symbol": symbol,
                "side": side,
                "input_amount": amount,
                "price": price,
                "output_amount": output_amount,
            })

            amount = output_amount

        return {
            "route_id": str(route.get("route_id", "")).strip(),
            "starting_value": float(starting_value),
            "gross_final_value": amount,
            "legs": executed_legs,
        }
