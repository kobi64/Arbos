"""
ArbOS™
EX-087
Live Route Valuation Engine
"""

import math


class LiveRouteValuationEngine:
    def __init__(self, market_data_provider):
        self._provider = market_data_provider

    def evaluate(self, route, starting_value):
        if route is None:
            raise ValueError("route is required")

        try:
            starting_value = float(starting_value)
        except (TypeError, ValueError):
            raise ValueError(
                "starting_value must be positive"
            )

        if (
            not math.isfinite(starting_value)
            or starting_value <= 0
        ):
            raise ValueError(
                "starting_value must be positive"
            )

        amount = starting_value
        executed_legs = []

        for index, leg in enumerate(
            route.get("legs") or [],
            start=1,
        ):
            symbol = leg.get("symbol")
            side = str(
                leg.get("side", "")
            ).strip().lower()

            if side == "buy":
                raw_price = self._provider.get_ask(
                    symbol
                )
            elif side == "sell":
                raw_price = self._provider.get_bid(
                    symbol
                )
            else:
                raise ValueError("invalid side")

            try:
                price = float(raw_price)
            except (TypeError, ValueError):
                raise ValueError(
                    "market price unavailable"
                )

            if (
                not math.isfinite(price)
                or price <= 0
            ):
                raise ValueError(
                    "market price unavailable"
                )

            if side == "buy":
                output_amount = amount / price
            else:
                output_amount = amount * price

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
            "route_id": str(
                route.get("route_id", "")
            ).strip(),
            "starting_value": starting_value,
            "gross_final_value": amount,
            "legs": executed_legs,
        }
