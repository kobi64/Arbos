"""
ArbOS™
EX-091
Order Book Liquidity & Slippage Engine
"""


class OrderBookLiquiditySlippageEngine:
    def evaluate(self, side, quantity, order_book):
        side = str(side).strip().lower()

        if side not in {"buy", "sell"}:
            raise ValueError("invalid side")

        try:
            quantity = float(quantity)
        except (TypeError, ValueError):
            quantity = 0.0

        if quantity <= 0:
            raise ValueError("quantity must be positive")

        levels = (
            order_book.get("asks")
            if side == "buy"
            else order_book.get("bids")
        ) or []

        if not levels:
            raise ValueError("order book unavailable")

        best_price = float(levels[0][0])
        remaining = quantity
        filled_quantity = 0.0
        total_value = 0.0

        for level in levels:
            price = float(level[0])
            available = float(level[1])

            if available <= 0:
                continue

            fill_quantity = min(remaining, available)
            total_value += fill_quantity * price
            filled_quantity += fill_quantity
            remaining -= fill_quantity

            if remaining <= 0:
                break

        average_price = (
            total_value / filled_quantity
            if filled_quantity > 0
            else 0.0
        )

        if side == "buy":
            slippage_percent = (
                (average_price - best_price) / best_price
            ) * 100
        else:
            slippage_percent = (
                (best_price - average_price) / best_price
            ) * 100

        filled = remaining <= 0

        return {
            "filled": filled,
            "reason": None if filled else "insufficient_liquidity",
            "requested_quantity": quantity,
            "filled_quantity": filled_quantity,
            "best_price": best_price,
            "average_price": average_price,
            "slippage_percent": slippage_percent,
            "total_value": total_value,
        }
