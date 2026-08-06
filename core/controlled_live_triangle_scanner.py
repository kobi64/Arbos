"""
ArbOS™
EX-115
Controlled Live Triangle Scanner
"""


class ControlledLiveTriangleScanner:
    def __init__(self, market_data_provider):
        self._provider = market_data_provider

    def scan(self, routes, starting_value):
        if starting_value <= 0:
            raise ValueError("starting_value must be positive")

        results = []

        for route in routes:
            amount = float(starting_value)
            legs = []

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

                legs.append({
                    "leg_number": index,
                    "symbol": symbol,
                    "side": side,
                    "price": price,
                    "input_amount": amount,
                    "output_amount": output_amount,
                })

                amount = output_amount

            final_value = amount
            net_profit = final_value - float(starting_value)
            profit_percent = (
                net_profit / float(starting_value)
            ) * 100.0

            results.append({
                "route_id": route.get("route_id"),
                "starting_value": float(starting_value),
                "final_value": final_value,
                "net_profit": net_profit,
                "profit_percent": profit_percent,
                "legs": legs,
                "paper_only": True,
                "live_order_submitted": False,
            })

        results.sort(
            key=lambda result: result["profit_percent"],
            reverse=True,
        )

        return results
