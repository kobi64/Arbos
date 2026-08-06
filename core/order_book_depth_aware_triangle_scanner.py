"""
ArbOS™
EX-117
Order Book Depth-Aware Triangle Scanner
"""

from exchanges.order_book_liquidity_slippage_engine import (
    OrderBookLiquiditySlippageEngine,
)


class OrderBookDepthAwareTriangleScanner:
    def __init__(self, order_book_provider):
        self._provider = order_book_provider
        self._engine = OrderBookLiquiditySlippageEngine()

    def scan_route(
        self,
        route,
        starting_value,
        fee_rate,
        max_slippage_percent,
    ):
        if starting_value <= 0:
            raise ValueError("starting_value must be positive")

        if fee_rate < 0:
            raise ValueError("fee_rate must be non-negative")

        if max_slippage_percent < 0:
            raise ValueError("max_slippage_percent cannot be negative")

        amount = float(starting_value)
        total_fee_amount = 0.0
        valued_legs = []

        for index, leg in enumerate(route.get("legs") or [], start=1):
            symbol = leg.get("symbol")
            side = str(leg.get("side", "")).strip().lower()
            order_book = self._provider.snapshot(symbol)

            best_price = (
                float(order_book["asks"][0][0])
                if side == "buy"
                else float(order_book["bids"][0][0])
            )

            quantity = (
                amount / best_price
                if side == "buy"
                else amount
            )

            depth = self._engine.evaluate(
                side=side,
                quantity=quantity,
                order_book=order_book,
            )

            if not depth["filled"]:
                return {
                    "route_id": route.get("route_id"),
                    "filled": False,
                    "reason": depth["reason"],
                    "legs": valued_legs,
                    "paper_only": True,
                    "live_order_submitted": False,
                }

            if depth["slippage_percent"] > max_slippage_percent:
                return {
                    "route_id": route.get("route_id"),
                    "filled": False,
                    "reason": "slippage_exceeded",
                    "legs": valued_legs,
                    "paper_only": True,
                    "live_order_submitted": False,
                }

            if side == "buy":
                gross_output = amount / depth["average_price"]
            else:
                gross_output = amount * depth["average_price"]

            fee_amount = gross_output * float(fee_rate)
            net_output = gross_output - fee_amount
            total_fee_amount += fee_amount

            valued_legs.append({
                "leg_number": index,
                "symbol": symbol,
                "side": side,
                "best_price": depth["best_price"],
                "average_price": depth["average_price"],
                "slippage_percent": depth["slippage_percent"],
                "fee_rate": float(fee_rate),
                "fee_amount": fee_amount,
                "net_output_amount": net_output,
            })

            amount = net_output

        net_final_value = amount
        net_profit = net_final_value - float(starting_value)
        net_profit_percent = (
            net_profit / float(starting_value)
        ) * 100.0

        max_leg_slippage_percent = max(
            (leg["slippage_percent"] for leg in valued_legs),
            default=0.0,
        )

        return {
            "route_id": route.get("route_id"),
            "filled": True,
            "reason": None,
            "starting_value": float(starting_value),
            "net_final_value": net_final_value,
            "net_profit": net_profit,
            "net_profit_percent": net_profit_percent,
            "total_fee_amount": total_fee_amount,
            "max_leg_slippage_percent": max_leg_slippage_percent,
            "legs": valued_legs,
            "paper_only": True,
            "live_order_submitted": False,
        }
