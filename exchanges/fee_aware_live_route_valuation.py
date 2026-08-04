"""
ArbOS™
EX-089
Fee-Aware Live Route Valuation
"""


class FeeAwareLiveRouteValuation:
    def __init__(self, market_data_provider):
        self._provider = market_data_provider

    def evaluate(self, route, starting_value):
        if route is None:
            raise ValueError("route is required")

        if starting_value <= 0:
            raise ValueError("starting_value must be positive")

        amount = float(starting_value)
        gross_without_fees = float(starting_value)
        valued_legs = []

        for index, leg in enumerate(route.get("legs") or [], start=1):
            symbol = leg.get("symbol")
            side = str(leg.get("side", "")).strip().lower()
            fee_rate = float(leg.get("fee_rate", 0.0))

            if fee_rate < 0:
                raise ValueError("fee_rate must be non-negative")

            if side == "buy":
                price = float(self._provider.get_ask(symbol))
                gross_output = amount / price
            elif side == "sell":
                price = float(self._provider.get_bid(symbol))
                gross_output = amount * price
            else:
                raise ValueError("invalid side")

            fee_amount = gross_output * fee_rate
            net_output = gross_output - fee_amount

            valued_legs.append({
                "leg_number": index,
                "symbol": symbol,
                "side": side,
                "input_amount": amount,
                "price": price,
                "gross_output_amount": gross_output,
                "fee_rate": fee_rate,
                "fee_amount": fee_amount,
                "net_output_amount": net_output,
            })

            amount = net_output

        fee_multiplier = 1.0
        for leg in valued_legs:
            fee_multiplier *= 1.0 - leg["fee_rate"]

        return {
            "route_id": str(route.get("route_id", "")).strip(),
            "starting_value": float(starting_value),
            "gross_final_value": amount,
            "total_fee_rate_effect": 1.0 - fee_multiplier,
            "legs": valued_legs,
        }
